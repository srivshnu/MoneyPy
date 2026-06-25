import importlib
import traceback

TEST_MODULES = [
    'test_loan_calc',
    'test_bank_comparison',
    'test_run',
    'test_prepayment',
    'test_multi_loan',
    'test_investment_calc',
]

def run():
    failures = 0
    for mod in TEST_MODULES:
        try:
            m = importlib.import_module(mod)
        except Exception:
            print(f"FAILED to import {mod}:")
            traceback.print_exc()
            failures += 1
            continue

        # collect callable tests by name prefix
        tests = [getattr(m, name) for name in dir(m) if name.startswith('test_') and callable(getattr(m, name))]
        for t in tests:
            try:
                # If test expects parameters (e.g., pytest parametrize), provide sensible defaults
                import inspect
                sig = inspect.signature(t)
                if len(sig.parameters) == 0:
                    t()
                else:
                    # supply sample values for known parametrized tests
                    sample_args_map = {
                        'test_schedule_consistency': (120000.0, 0.0, 12),
                    }
                    if t.__name__ in sample_args_map:
                        t(*sample_args_map[t.__name__])
                    else:
                        # naive fallback: try calling with zeros / small defaults
                        params = []
                        for name, p in sig.parameters.items():
                            params.append(0 if p.annotation in (int, float) or p.default == inspect._empty else p.default)
                        t(*params)
                print(f"ok: {mod}.{t.__name__}")
            except AssertionError:
                print(f"FAILED: {mod}.{t.__name__} (AssertionError)")
                traceback.print_exc()
                failures += 1
            except Exception:
                print(f"ERROR: {mod}.{t.__name__}")
                traceback.print_exc()
                failures += 1

    if failures:
        print(f"\nTESTS FINISHED: {failures} failures/errors")
        raise SystemExit(1)
    else:
        print("\nALL TESTS PASSED")

if __name__ == '__main__':
    run()
