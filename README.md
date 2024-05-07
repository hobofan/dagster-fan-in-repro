# Dagster bug reproduction - Fan-in in graph used in mapping DynamicOut

## How to run

```bash
poetry install
poetry run dagster dev
```

- Go to UI -> Try to trigger a run for the job `many_job` -> 500 error in console and no run created (error below)
- As comparison, `single_job` where the `graph` is not used in a mapping works fine

## Error messages

Direct error response:
```json
{
  "data": {
    "launchPipelineExecution": {
      "message": "dagster._check.CheckError: Failure condition: Unexpected dynamic output dependency in regular fan in, should have been caught at definition time.\n",
      "stack": [
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_grpc/impl.py\", line 534, in get_external_execution_plan_snapshot\n    create_execution_plan(\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/api.py\", line 730, in create_execution_plan\n    return ExecutionPlan.build(\n           ^^^^^^^^^^^^^^^^^^^^\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 1056, in build\n    ).build()\n      ^^^^^^^\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 182, in build\n    self._build_from_sorted_nodes(\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 354, in _build_from_sorted_nodes\n    self._build_from_sorted_nodes(\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 354, in _build_from_sorted_nodes\n    self._build_from_sorted_nodes(\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 258, in _build_from_sorted_nodes\n    step_input_source = get_step_input_source(\n                        ^^^^^^^^^^^^^^^^^^^^^^\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 469, in get_step_input_source\n    return _step_input_source_from_multi_dep_def(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 559, in _step_input_source_from_multi_dep_def\n    check.failed(\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_check/__init__.py\", line 1606, in failed\n    raise CheckError(f\"Failure condition: {desc}\")\n"
      ],
      "errorChain": [],
      "__typename": "PythonError"
    }
  }
}
```

Error response after commenting out check in plan.py gives a bit more context:
```json
{
  "data": {
    "launchPipelineExecution": {
      "message": "dagster._check.ParameterCheckError: Param \"step_output_handle\" is not a StepOutputHandle. Got UnresolvedStepOutputHandle(unresolved_step_handle=UnresolvedStepHandle(node_handle=NodeHandle(name='duplicate_foo_text', parent=NodeHandle(name='analyze_foo_or_bar', parent=NodeHandle(name='analyzed_many', parent=None)))), output_name='unified', resolved_by_step_key='analyzed_many.many_foo_bar_fanout', resolved_by_output_name='result') which is type <class 'dagster._core.execution.plan.outputs.UnresolvedStepOutputHandle'>.\n",
      "stack": [
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_grpc/impl.py\", line 534, in get_external_execution_plan_snapshot\n    create_execution_plan(\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/api.py\", line 730, in create_execution_plan\n    return ExecutionPlan.build(\n           ^^^^^^^^^^^^^^^^^^^^\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 1056, in build\n    ).build()\n      ^^^^^^^\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 182, in build\n    self._build_from_sorted_nodes(\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 354, in _build_from_sorted_nodes\n    self._build_from_sorted_nodes(\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 354, in _build_from_sorted_nodes\n    self._build_from_sorted_nodes(\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 258, in _build_from_sorted_nodes\n    step_input_source = get_step_input_source(\n                        ^^^^^^^^^^^^^^^^^^^^^^\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 469, in get_step_input_source\n    return _step_input_source_from_multi_dep_def(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/plan.py\", line 565, in _step_input_source_from_multi_dep_def\n    FromStepOutput(\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_core/execution/plan/inputs.py\", line 413, in __new__\n    step_output_handle=check.inst_param(\n                       ^^^^^^^^^^^^^^^^^\n",
        "  File \"/Users/hobofan/Library/Caches/pypoetry/virtualenvs/dagster-fan-in-repro-J-Y5pXQV-py3.11/lib/python3.11/site-packages/dagster/_check/__init__.py\", line 638, in inst_param\n    raise _param_type_mismatch_exception(\n"
      ],
      "errorChain": [],
      "__typename": "PythonError"
    }
  }
}
```