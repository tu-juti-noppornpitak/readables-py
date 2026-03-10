import os
from textwrap import dedent
from unittest import TestCase

from readables.env import RequiredEnvironmentVariable, EnvironmentVariableManager, MarkdownExporter, EnvFileExporter


class TestUnit(TestCase):
    def tearDown(self):
        os.environ['READABLES_ENV_ALLOW_UNSET_REQUIRED'] = 'false'

    def _revert_env_var_to_original(self, env, value):
        if value is None:
            if env in os.environ:
                del os.environ[env]
        else:
            os.environ[env] = value

    def test_required_flag(self):
        original_value = os.getenv('T_ALPHA')

        evm = EnvironmentVariableManager()

        with self.assertRaises(RequiredEnvironmentVariable):
            evm.required_env('T_ALPHA')

        expected_value = 'foo'
        os.environ['T_ALPHA'] = expected_value
        self.addCleanup(lambda: self._revert_env_var_to_original('T_ALPHA', original_value))

        self.assertEqual(evm.required_env('T_ALPHA'), expected_value)

        expected_value = 123
        os.environ['T_ALPHA'] = str(expected_value)
        self.addCleanup(lambda: self._revert_env_var_to_original('T_ALPHA', original_value))

        self.assertEqual(evm.required_env('T_ALPHA', kind=int), expected_value)

    def test_optional_flag_without_changing_default_value(self):
        evm = EnvironmentVariableManager()
        self.assertFalse(evm.optional_flag('T_BETA'))
        self.assertTrue(evm.optional_flag('T_BETA', default=True))

    def test_markdown_export(self):
        os.environ['READABLES_ENV_ALLOW_UNSET_REQUIRED'] = 'true'

        evm = EnvironmentVariableManager()
        evm.required_env('MOCK_ALPHA', help='a' * 120 + '\n\n' + 'a' * 90)
        evm.optional_env('MOCK_BETA', 'beta', help='b' * 120 + '\n\n' + 'b' * 90)
        evm.flag('MOCK_CHARLIE', help='c' * 120 + '\n\n' + 'c' * 90)

        output = EnvFileExporter.export(evm.variables)

        self.assertEqual(
            dedent("""
            # [REQUIRED variable]
# MOCK_ALPHA
# 
# > Interpreted as builtins.str
# 
# aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
# aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
# 
# aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
# aaaaaaaaaaaaaaaaaaaa
# 
MOCK_ALPHA=

# [OPTIONAL variable]
# MOCK_BETA
# 
# > Interpreted as builtins.str
# 
# bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
# bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
# 
# bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
# bbbbbbbbbbbbbbbbbbbb
# 
#MOCK_BETA=beta

# [OPTIONAL flag]
# MOCK_CHARLIE
# 
# > Interpreted as builtins.str
# 
# cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
# cccccccccccccccccccccccccccccccccccccccccccccccccc
# 
# cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
# cccccccccccccccccccc
# 
#MOCK_CHARLIE=false
            """.strip()),
            output
        )
