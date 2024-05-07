from typing import Optional, List

from dagster import Definitions, op, In, Out, graph, GraphOut, usable_as_dagster_type, asset, graph_asset, Output, \
    OpExecutionContext, DynamicOut, define_asset_job
from pydantic import BaseModel


@usable_as_dagster_type
class FooOrBar(BaseModel):
    id: str
    foo: Optional[str] = None
    bar: Optional[str] = None


@usable_as_dagster_type
class Foo(BaseModel):
    foo: str


@usable_as_dagster_type
class Bar(BaseModel):
    bar: str


@usable_as_dagster_type
class Unified(BaseModel):
    foo_or_bar: str


@op(
    ins={"thing": In(dagster_type=FooOrBar)},
    out={
        "foo": Out(is_required=False),
        "bar": Out(is_required=False),
    },
)
def branch_for_extraction(thing: FooOrBar):
    if thing.foo:
        yield Output(Foo(foo=thing.foo), output_name="foo")
    elif thing.bar:
        yield Output(Bar(bar=thing.bar), output_name="bar")


@op(
    ins={"foo": In(dagster_type=Foo)},
    out={"unified": Out(dagster_type=Unified)},
)
def duplicate_foo_text(foo: Foo):
    return Unified(foo_or_bar=f"{foo.foo}{foo.foo}")


@op(
    ins={"bar": In(dagster_type=Bar)},
    out={"unified": Out(dagster_type=Unified)},
)
def erase_bar_text(bar: Bar):
    return Unified(foo_or_bar="")

@op(
    ins={"unifieds": In(dagster_type=List[Unified])},
    out={"unified": Out(dagster_type=Unified)},
)
def fan_in_unified(context: OpExecutionContext, unifieds: List[Unified]):
    # Return first present value, as only one branch will be taken
    for unified in unifieds:
        if unified:
            context.log.info(f"Returning {unified}")
            return unified

@graph(
    ins={"foo_or_bar": In()},
    out={"unified": GraphOut()},
)
def analyze_foo_or_bar(foo_or_bar):
    foo, bar = branch_for_extraction(foo_or_bar)
    processed_foo = duplicate_foo_text(foo)
    processed_bar = erase_bar_text(bar)

    return fan_in_unified([processed_foo, processed_bar])

### Test case for single invocation of the `analyze_foo_or_bar` graph -> Works
@asset
def single_foo_bar():
    return FooOrBar(id="1", foo="foo")


@graph_asset
def analyzed_foo_bar(single_foo_bar):
    return analyze_foo_or_bar(single_foo_bar)

single_job = define_asset_job(
    name="single_job", selection="*analyzed_foo_bar"
)

### Test case for mapped invocation of the `analyze_foo_or_bar` graph -> Doesn't work
@asset
def many_foo_bar() -> List[FooOrBar]:
    return [
        FooOrBar(id="1", foo="foo"),
        FooOrBar(id="2", bar="bar"),
        FooOrBar(id="3", foo="baz"),
    ]

@op(
    ins={"many": In(dagster_type=List[FooOrBar])},
    out={"result": DynamicOut(dagster_type=FooOrBar)}
)
def many_foo_bar_fanout(many: List[FooOrBar]):
    for foo_or_bar in many:
        yield Output(foo_or_bar, mapping_key=foo_or_bar.id)

@op
def many_fan_in(many: List[Unified]) -> List[Unified]:
    return many

@graph_asset
def analyzed_many(many_foo_bar):
    return many_fan_in(many_foo_bar_fanout(many_foo_bar).map(analyze_foo_or_bar).collect())


many_job = define_asset_job(
    name="many_job", selection="*analyzed_many"
)

defs = Definitions(
    assets=[single_foo_bar, analyzed_foo_bar, many_foo_bar, analyzed_many],
    jobs=[single_job, many_job]
)