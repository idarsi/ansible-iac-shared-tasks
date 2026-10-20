"""Focused regression test for matching semanage file-context output."""

import unittest

from ansible.plugins.filter.core import regex_escape
from ansible.plugins.test.core import search
from jinja2 import Environment


class FileSelinuxRuleTest(unittest.TestCase):
    def test_semanage_output_with_file_path_and_trailing_space_matches(self):
        path = "/var/www/selinux.example.org/html/selinux-check.txt"
        setype = "httpd_sys_content_t"
        stdout = (
            f"{path} all files          "
            "system_u:object_r:httpd_sys_content_t:s0 "
        )
        environment = Environment()
        environment.filters["regex_escape"] = regex_escape
        environment.tests["search"] = search

        exists_template = environment.from_string(
            "{{ stdout is search('^' ~ (path | regex_escape) "
            "~ '[ \\\\t]+', multiline=True) }}"
        )
        matches_template = environment.from_string(
            "{{ stdout is search('^' ~ (path | regex_escape) "
            "~ '[ \\\\t]+.*' ~ (setype | regex_escape) "
            "~ '.*$', multiline=True) }}"
        )

        self.assertEqual(
            exists_template.render(stdout=stdout, path=path), "True"
        )
        self.assertEqual(
            matches_template.render(stdout=stdout, path=path, setype=setype),
            "True",
        )


if __name__ == "__main__":
    unittest.main()
