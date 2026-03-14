from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "ledger_excel.py"


class LedgerExcelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "Ledger"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_cli(self, *args: str):
        proc = subprocess.run(
            ["uv", "run", str(SCRIPT_PATH), *args],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(proc.stdout)

    def run_cli_raw(self, *args: str):
        return subprocess.run(
            ["uv", "run", str(SCRIPT_PATH), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_bootstrap_creates_config_and_month_workbook(self) -> None:
        result = self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        self.assertEqual(2, len(result))
        self.assertTrue((self.root / "bookkeeping-config.xlsx").exists())
        self.assertTrue((self.root / "2026" / "2026-03.xlsx").exists())

    def test_add_transaction_auto_classifies_from_note(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        result = self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-11",
            "--direction", "expense",
            "--amount", "18.50",
            "--account", "支付宝",
            "--tags", "日常",
            "--note", "奶茶",
        )
        self.assertEqual("auto", result["category_source"])
        self.assertEqual("餐饮", result["level1"])
        self.assertEqual("零食饮料", result["level2"])

    def test_apply_recurring_writes_month_only_once(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        self.run_cli(
            "add-recurring",
            "--root", str(self.root),
            "--name", "Claude 月订阅",
            "--direction", "expense",
            "--amount", "140",
            "--account", "支付宝",
            "--level1", "数码数字",
            "--level2", "服务订阅",
            "--tags", "软件,订阅",
            "--note", "Claude Pro",
            "--merchant", "Claude",
            "--frequency", "monthly",
            "--day", "11",
            "--start-date", "2026-03-11",
        )
        first = self.run_cli("apply-recurring", "--root", str(self.root), "--month", "2026-04")
        second = self.run_cli("apply-recurring", "--root", str(self.root), "--month", "2026-04")
        self.assertEqual(1, len(first))
        self.assertEqual([], second)

    def test_limit_report_sums_tagged_expense(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        self.run_cli("set-limit", "--root", str(self.root), "--year", "2026", "--tag", "摄影", "--amount", "1000", "--note", "年度摄影额度")
        self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-11",
            "--direction", "expense",
            "--amount", "288.88",
            "--account", "银行卡",
            "--level1", "兴趣爱好",
            "--level2", "摄影",
            "--tags", "摄影",
            "--note", "相机清洁服务",
        )
        report = self.run_cli("limit-report", "--root", str(self.root), "--year", "2026")
        self.assertEqual("摄影", report[0]["tag"])
        self.assertEqual("288.88", report[0]["spent_amount"])
        self.assertEqual("711.12", report[0]["remaining_amount"])

    def test_query_filters_by_category_note_and_date_range(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-02",
            "--direction", "expense",
            "--amount", "499.00",
            "--account", "银行卡",
            "--level1", "数码数字",
            "--level2", "数码产品",
            "--tags", "摄影,器材",
            "--note", "摄影补光灯",
        )
        self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-05",
            "--direction", "expense",
            "--amount", "39.90",
            "--account", "支付宝",
            "--level1", "餐饮",
            "--level2", "零食饮料",
            "--tags", "日常",
            "--note", "咖啡",
        )
        self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-04-01",
            "--direction", "expense",
            "--amount", "129.00",
            "--account", "银行卡",
            "--level1", "数码数字",
            "--level2", "数码产品",
            "--tags", "摄影",
            "--note", "摄影电池",
        )
        result = self.run_cli(
            "query",
            "--root", str(self.root),
            "--direction", "expense",
            "--date-from", "2026-03-01",
            "--date-to", "2026-03-31",
            "--level1", "数码数字",
            "--level2", "数码产品",
            "--note-contains", "摄影",
        )
        self.assertEqual(1, result["count"])
        self.assertEqual("499.00", result["transactions"][0]["amount"])
        self.assertEqual("摄影补光灯", result["transactions"][0]["note"])

    def test_stats_support_compound_filters(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-02",
            "--direction", "expense",
            "--amount", "499.00",
            "--account", "银行卡",
            "--level1", "数码数字",
            "--level2", "数码产品",
            "--tags", "摄影,器材",
            "--note", "摄影补光灯",
        )
        self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-10",
            "--direction", "expense",
            "--amount", "129.00",
            "--account", "银行卡",
            "--level1", "数码数字",
            "--level2", "数码产品",
            "--tags", "摄影",
            "--note", "摄影电池",
        )
        self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-12",
            "--direction", "expense",
            "--amount", "199.00",
            "--account", "银行卡",
            "--level1", "数码数字",
            "--level2", "软件买断",
            "--tags", "摄影",
            "--note", "修图软件授权",
        )
        result = self.run_cli(
            "stats",
            "--root", str(self.root),
            "--direction", "expense",
            "--date-from", "2026-03-01",
            "--date-to", "2026-03-31",
            "--level1", "数码数字",
            "--level2", "数码产品",
            "--tag", "摄影",
            "--note-contains", "摄影",
            "--group-by", "month",
        )
        self.assertEqual(2, result["count"])
        self.assertEqual("628.00", result["total_amount"])
        self.assertEqual("2026-03", result["groups"][0]["group"])
        self.assertEqual("628.00", result["groups"][0]["total_amount"])

    def test_update_can_modify_batch_transactions(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        first = self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-02",
            "--direction", "expense",
            "--amount", "88.00",
            "--account", "支付宝",
            "--level1", "数码数字",
            "--level2", "数码产品",
            "--tags", "摄影",
            "--note", "镜头清洁",
        )
        second = self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-03",
            "--direction", "expense",
            "--amount", "66.00",
            "--account", "支付宝",
            "--level1", "数码数字",
            "--level2", "数码产品",
            "--tags", "摄影",
            "--note", "镜头贴膜",
        )
        result = self.run_cli(
            "update",
            "--root", str(self.root),
            "--id", first["transaction_id"],
            "--id", second["transaction_id"],
            "--set-note", "摄影配件",
            "--add-tags", "器材",
            "--allow-multiple",
        )
        self.assertEqual(2, result["updated_count"])
        queried = self.run_cli(
            "query",
            "--root", str(self.root),
            "--tag", "器材",
            "--note-contains", "摄影配件",
        )
        self.assertEqual(2, queried["count"])

    def test_service_subscription_creates_tracking_row(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-11",
            "--direction", "expense",
            "--amount", "98.00",
            "--account", "支付宝",
            "--level1", "数码数字",
            "--level2", "服务订阅",
            "--tags", "软件,订阅",
            "--merchant", "Pixlr",
            "--note", "Pixlr 月订阅",
            "--subscription-cycle", "monthly",
        )
        report = self.run_cli("subscription-report", "--root", str(self.root))
        self.assertEqual(1, report["count"])
        self.assertEqual("Pixlr", report["subscriptions"][0]["name"])
        self.assertEqual("2026-03-11", report["subscriptions"][0]["start_date"])
        self.assertEqual("2026-04-11", report["subscriptions"][0]["renewal_date"])

    def test_help_includes_side_effect_labels(self) -> None:
        proc = self.run_cli_raw("--help")
        self.assertEqual(0, proc.returncode)
        self.assertIn("[mutates]", proc.stdout)
        self.assertIn("[read-request-may-mutate]", proc.stdout)

    def test_command_fails_fast_when_lock_is_held(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        lock_holder = subprocess.Popen(
            [
                "python3",
                "-c",
                (
                    "import fcntl,time,pathlib;"
                    f"p=pathlib.Path(r'{self.root}')/'.ledger.lock';"
                    "p.parent.mkdir(parents=True,exist_ok=True);"
                    "f=open(p,'a+');"
                    "fcntl.flock(f.fileno(), fcntl.LOCK_EX);"
                    "time.sleep(2)"
                ),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            proc = self.run_cli_raw("query", "--root", str(self.root), "--month", "2026-03")
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("ledger is busy", proc.stderr + proc.stdout)
        finally:
            lock_holder.terminate()
            lock_holder.wait(timeout=5)

    def test_repair_month_dry_run_and_execute(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        month_file = self.root / "2026" / "2026-03.xlsx"
        month_file.write_text("not-a-zip", encoding="utf-8")
        dry_run = self.run_cli("repair-month", "--root", str(self.root), "--month", "2026-03")
        self.assertTrue(dry_run["is_corrupted"])
        self.assertEqual("dry-run", dry_run["action"])
        repaired = self.run_cli("repair-month", "--root", str(self.root), "--month", "2026-03", "--execute")
        self.assertEqual("repaired", repaired["action"])
        self.assertTrue((self.root / "2026" / "2026-03.xlsx").exists())
        self.assertTrue(repaired["backup_path"].endswith(".badzip"))

    def test_source_uses_single_atomic_save_callsite(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertIn("def save_workbook_atomic", source)
        self.assertEqual(1, source.count(".save("))

    def test_limit_report_ignores_backup_and_malformed_month_files(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        self.run_cli("set-limit", "--root", str(self.root), "--year", "2026", "--tag", "摄影", "--amount", "1000")
        self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-11",
            "--direction", "expense",
            "--amount", "200.00",
            "--account", "银行卡",
            "--level1", "兴趣爱好",
            "--level2", "摄影",
            "--tags", "摄影",
            "--note", "测试消费",
        )
        year_dir = self.root / "2026"
        (year_dir / "2026-03.corrupted-20260314.xlsx").write_text("not-a-zip", encoding="utf-8")
        (year_dir / "2026-13.xlsx").write_text("not-a-zip", encoding="utf-8")
        (year_dir / "notes.xlsx").write_text("not-a-zip", encoding="utf-8")
        (year_dir / "2026-04.xlsx").write_text("not-a-zip", encoding="utf-8")

        report = self.run_cli("limit-report", "--root", str(self.root), "--year", "2026")
        self.assertEqual("200.00", report[0]["spent_amount"])

    def test_query_skips_malformed_month_workbook(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-11",
            "--direction", "expense",
            "--amount", "88.00",
            "--account", "支付宝",
            "--level1", "数码数字",
            "--level2", "数码产品",
            "--note", "正常记录",
        )
        year_dir = self.root / "2026"
        (year_dir / "2026-04.xlsx").write_text("not-a-zip", encoding="utf-8")

        result = self.run_cli("query", "--root", str(self.root), "--month", "2026-03")
        self.assertEqual(1, result["count"])

    def test_add_account_and_alias_can_be_used_for_entry(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        add_result = self.run_cli(
            "add-account",
            "--root", str(self.root),
            "--account", "招行储蓄卡",
            "--account-type", "bank",
            "--alias", "招行卡",
        )
        self.assertEqual("招行储蓄卡", add_result["account"])
        self.assertEqual(["招行卡"], add_result["aliases"])

        accounts = self.run_cli("list-accounts", "--root", str(self.root))
        account_names = [item["account"] for item in accounts["accounts"]]
        self.assertIn("招行储蓄卡", account_names)
        self.assertEqual("招行储蓄卡", accounts["alias_map"]["招行卡"])

        tx = self.run_cli(
            "add",
            "--root", str(self.root),
            "--date", "2026-03-12",
            "--direction", "income",
            "--amount", "100.00",
            "--account", "招行卡",
            "--level1", "收入",
            "--level2", "其他收入",
            "--note", "别名入账",
        )
        self.assertEqual("招行储蓄卡", tx["account"])

    def test_preflight_reports_month_corruption(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        month_file = self.root / "2026" / "2026-03.xlsx"
        month_file.write_text("broken", encoding="utf-8")
        result = self.run_cli("preflight", "--root", str(self.root), "--month", "2026-03")
        self.assertFalse(result["ok"])
        issue_codes = [item["code"] for item in result["issues"]]
        self.assertIn("invalid_month_workbook", issue_codes)

    def test_batch_ingest_imports_json_transactions(self) -> None:
        self.run_cli("bootstrap", "--root", str(self.root), "--month", "2026-03")
        payload = [
            {
                "date": "2026-03-10",
                "direction": "income",
                "amount": "5000",
                "account": "银行卡",
                "level1": "收入",
                "level2": "工资",
                "note": "批量工资",
            },
            {
                "date": "2026-03-11",
                "direction": "expense",
                "amount": "50",
                "account": "支付宝",
                "level1": "餐饮",
                "level2": "零食饮料",
                "note": "批量奶茶",
            },
            {
                "date": "2026-03-12",
                "direction": "transfer",
                "amount": "200",
                "from_account": "银行卡",
                "to_account": "微信",
                "note": "批量转账",
            },
        ]
        payload_path = self.root / "batch.json"
        payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = self.run_cli(
            "batch-ingest",
            "--root", str(self.root),
            "--file", str(payload_path),
            "--month", "2026-03",
        )
        self.assertEqual(3, result["imported_count"])
        queried = self.run_cli("query", "--root", str(self.root), "--month", "2026-03")
        self.assertEqual(3, queried["count"])


if __name__ == "__main__":
    unittest.main()
