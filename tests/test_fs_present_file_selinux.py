"""Focused regression test for matching semanage file-context output."""

import unittest
from pathlib import Path

import yaml
from ansible.plugins.filter.core import regex_escape
from ansible.plugins.test.core import search
from jinja2 import Environment


class FileSelinuxRuleTest(unittest.TestCase):
    def test_semanage_add_and_modify_tasks_use_escaped_path_argv(self):
        task_file = Path(__file__).resolve().parents[1] / "fs_present_file.yml"
        tasks = yaml.safe_load(task_file.read_text(encoding="utf-8"))
        path = "/var/www/selinux.example.org/html/selinux-check.txt"
        expected_path = r"/var/www/selinux\.example\.org/html/selinux\-check\.txt"

        for task_name, operation in (
            ("Adding SELinux fcontext rule for file", "-a"),
            ("Modifying SELinux fcontext rule for file", "-m"),
        ):
            with self.subTest(task=task_name):
                task = next(task for task in tasks if task.get("name") == task_name)
                argv = task["ansible.builtin.command"]["argv"]

                self.assertEqual(argv[0:3], ["semanage", "fcontext", operation])
                self.assertEqual(
                    argv[-1], "{{ iac_fs_file_record.path | regex_escape }}"
                )
                self.assertEqual(regex_escape(path), expected_path)

    def test_generated_semanage_rule_escapes_dotted_file_path(self):
        path = "/var/www/selinux.example.org/html/selinux-check.txt"
        environment = Environment()
        environment.filters["regex_escape"] = regex_escape

        rule_template = environment.from_string(
            "{{ path | regex_escape }}"
        )

        self.assertEqual(
            rule_template.render(path=path),
            r"/var/www/selinux\.example\.org/html/selinux\-check\.txt",
        )

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
