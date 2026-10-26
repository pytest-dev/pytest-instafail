pytest_plugins = "pytester"
import pytest


class Option:
    def __init__(self, verbose=False, quiet=False, n=None):
        self.verbose = verbose
        self.quiet = quiet
        self.n = n

    @property
    def args(self):
        l = ['--instafail']
        if self.verbose:
            l.append('-v')
        if self.quiet:
            l.append('-q')
        if self.n is not None:
            l.extend(['-n', str(self.n)])
        return l


@pytest.fixture(params=['normal', '1 worker', '2 worker'])
def n(request):
    return {
        'normal': None,
        '1 worker': 1,
        '2 worker': 2,
    }[request.param]


@pytest.fixture(params=['default', 'verbose', 'quiet'])
def option(request, n):
    return {
        "default": Option(verbose=False, n=n),
        "verbose": Option(verbose=True, n=n),
        "quiet": Option(quiet=True, n=n),
    }[request.param]


class TestInstafailingTerminalReporter:
    @pytest.mark.parametrize('workers', [1, 2])
    def test_worker_option_runs_on_xdist_workers(self, testdir, workers):
        testdir.makepyfile(
            """
            def test_worker(request):
                assert hasattr(request.config, 'workerinput')
            """
        )
        result = testdir.runpytest(*Option(n=workers).args)
        result.assert_outcomes(passed=1)

    def test_fail(self, testdir, option):
        testdir.makepyfile(
            """
            import pytest
            def test_func():
                assert 0
            """
        )
        result = testdir.runpytest(*option.args)
        if option.verbose:
            result.stdout.fnmatch_lines([
                ("*FAILED test_fail.py::test_func*" if option.n is not None
                 else "*test_fail.py:*:*test_func*FAIL*"),
                "* test_func *",
                "    def test_func():",
                ">       assert 0",
                "E       assert 0",
            ])
        elif option.quiet or option.n is not None:
            result.stdout.fnmatch_lines([
                "F",
                "* test_func *",
                "    def test_func():",
                ">       assert 0",
                "E       assert 0",
            ])
        else:
            result.stdout.fnmatch_lines([
                "*test_fail.py F",
                "* test_func *",
                "    def test_func():",
                ">       assert 0",
                "E       assert 0",
            ])

    def test_fail_fail(self, testdir, option):
        testdir.makepyfile(
            """
            import pytest
            def test_func():
                assert 0
            def test_func2():
                assert 0
            """
        )
        result = testdir.runpytest(*option.args)
        if option.n is not None:
            result.assert_outcomes(failed=2)
            for name in ('test_func', 'test_func2'):
                result.stdout.fnmatch_lines([
                    "* %s *" % name,
                    "    def %s():" % name,
                    ">       assert 0",
                    "E       assert 0",
                ])
                if option.verbose:
                    result.stdout.fnmatch_lines([
                        "*FAILED test_fail_fail.py::%s*" % name,
                    ])
            return
        if option.verbose:
            result.stdout.fnmatch_lines([
                "*test_fail_fail.py:*:*test_func*FAIL*",
                "* test_func *",
                "    def test_func():",
                ">       assert 0",
                "E       assert 0",
                "test_fail_fail.py:3: AssertionError",
                "",
                "*test_fail_fail.py:*:*test_func2*FAIL*",
                "* test_func2 *",
                "    def test_func2():",
                ">       assert 0",
                "E       assert 0",
            ])
        elif option.quiet:
            result.stdout.fnmatch_lines([
                "F",
                "* test_func *",
                "    def test_func():",
                ">       assert 0",
                "E       assert 0",
                "F",
                "* test_func2 *",
                "    def test_func2():",
                ">       assert 0",
                "E       assert 0",
            ])
        else:
            result.stdout.fnmatch_lines([
                "*test_fail_fail.py F",
                "* test_func *",
                "    def test_func():",
                ">       assert 0",
                "E       assert 0",
                "*test_fail_fail.py F",
                "* test_func2 *",
                "    def test_func2():",
                ">       assert 0",
                "E       assert 0",
            ])

    def test_error_in_setup_then_pass(self, testdir, option):
        testdir.makepyfile(
            """
            def setup_function(function):
                print ("setup func")
                if function is test_nada:
                    assert 0
            def test_nada():
                pass
            def test_zip():
                pass
            """
        )
        result = testdir.runpytest(*option.args)

        if option.n is not None:
            result.assert_outcomes(passed=1, errors=1)
            result.stdout.fnmatch_lines([
                "*ERROR at setup of test_nada*",
                "*setup_function(function):*",
                "*if function is test_nada:*",
                "*assert 0*",
                "test_error_in_setup_then_pass.py:4: AssertionError",
                "*Captured stdout setup*",
                "setup func",
            ])
            if option.verbose:
                result.stdout.fnmatch_lines_random([
                    "*ERROR test_error_in_setup_then_pass.py::test_nada*",
                    "*PASSED test_error_in_setup_then_pass.py::test_zip*",
                ])
            return
        if option.verbose:
            result.stdout.fnmatch_lines([
                "*test_error_in_setup_then_pass.py:*:*test_nada*ERROR*",
                "*ERROR at setup of test_nada*",
                "*setup_function(function):*",
                "*setup func*",
                "*assert 0*",
                "test_error_in_setup_then_pass.py:4: AssertionError",
                "",
                "*test_error_in_setup_then_pass.py:*:*test_zip*PASSED*",
                "*1 error*",
            ])
        elif option.quiet:
            result.stdout.fnmatch_lines([
                "E",
                "*ERROR at setup of test_nada*",
                "*setup_function(function):*",
                "*setup func*",
                "*assert 0*",
                "test_error_in_setup_then_pass.py:4: AssertionError",
                ".*",
            ])
        else:
            result.stdout.fnmatch_lines([
                "*test_error_in_setup_then_pass.py E",
                "*ERROR at setup of test_nada*",
                "*setup_function(function):*",
                "*setup func*",
                "*assert 0*",
                "test_error_in_setup_then_pass.py:4: AssertionError",
                "",
                "*test_error_in_setup_then_pass.py .*",
                "*1 error*",
            ])
        assert result.ret != 0

    def test_error_in_teardown_then_pass(self, testdir, option):
        testdir.makepyfile(
            """
            def teardown_function(function):
                print ("teardown func")
                if function is test_nada:
                    assert 0
            def test_nada():
                pass
            def test_zip():
                pass
            """
        )
        result = testdir.runpytest(*option.args)

        if option.n is not None:
            result.assert_outcomes(passed=2, errors=1)
            result.stdout.fnmatch_lines([
                "*ERROR at teardown of test_nada*",
                "*teardown_function(function):*",
                "*if function is test_nada:*",
                "*assert 0*",
                "test_error_in_teardown_then_pass.py:4: AssertionError",
                "*Captured stdout teardown*",
                "teardown func",
            ])
            if option.verbose:
                result.stdout.fnmatch_lines_random([
                    "*ERROR test_error_in_teardown_then_pass.py::test_nada*",
                    "*PASSED test_error_in_teardown_then_pass.py::test_zip*",
                ])
            return
        if option.verbose:
            result.stdout.fnmatch_lines([
                "*test_error_in_teardown_then_pass.py:*:*test_nada*ERROR*",
                "*ERROR at teardown of test_nada*",
                "*teardown_function(function):*",
                "*teardown func*",
                "*assert 0*",
                "test_error_in_teardown_then_pass.py:4: AssertionError",
                "",
                "*test_error_in_teardown_then_pass.py:*:*test_zip*PASSED*",
                "*1 error*",
            ])
        elif option.quiet:
            result.stdout.fnmatch_lines([
                ".E",
                "*ERROR at teardown of test_nada*",
                "*teardown_function(function):*",
                "*teardown func*",
                "*assert 0*",
                "test_error_in_teardown_then_pass.py:4: AssertionError",
                ".*",
            ])
        else:
            result.stdout.fnmatch_lines([
                "*test_error_in_teardown_then_pass.py .E",
                "*ERROR at teardown of test_nada*",
                "*teardown_function(function):*",
                "*teardown func*",
                "*assert 0*",
                "test_error_in_teardown_then_pass.py:4: AssertionError",
                "",
                "*test_error_in_teardown_then_pass.py .*",
                "*1 error*",
            ])
        assert result.ret != 0

    def test_collect_error(self, testdir, option):
        testdir.makepyfile("""raise ValueError(0)""")
        result = testdir.runpytest(*option.args)
        result.stdout.fnmatch_lines([
            "*ERROR collecting test_collect_error.py*",
            "test_collect_error.py:1: in <module>",
            "*   raise ValueError(0)",
            "E   ValueError: 0",
        ])
        if option.n is not None:
            result.assert_outcomes(errors=option.n)
        elif not option.quiet:
            result.stdout.fnmatch_lines([
                "collected 0 items / 1 error*",
            ])

    def test_print_stacktrace_once_with_pdb(self, testdir, request, option):
        if option.n is not None:
            pytest.skip("--pdb is incompatible with xdist workers")
        test_file = testdir.makepyfile(
            """
            def test_func():
                assert 0
            """
        )

        args = option.args
        args.append(" --pdb %s" % test_file)

        child = testdir.spawn_pytest(' '.join(args))
        child.expect('>+ traceback >+')

        assert b'E       assert 0' not in child.before

        child.expect('(Pdb)')
        child.sendeof()
        if child.isalive():
            child.wait()

    def test_xfail_unexpected_success(self, testdir, option):
        testdir.makepyfile(
            """
            import pytest
            @pytest.mark.xfail
            def test_func():
                pass
            """
        )
        result = testdir.runpytest(*option.args)
        if option.verbose:
            result.stdout.fnmatch_lines([
                ("*XPASS test_xfail_unexpected_success.py::test_func*"
                 if option.n is not None
                 else "test_xfail_unexpected_success.py:*:*test_func XPASS*")
            ])
        elif option.quiet or option.n is not None:
            result.stdout.fnmatch_lines([
                "X*"
            ])
        else:
            result.stdout.fnmatch_lines([
                "test_xfail_unexpected_success.py X*"
            ])
        assert "INTERNALERROR" not in result.stdout.str()
