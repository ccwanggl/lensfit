import { FileSpreadsheet } from "lucide-react";
import { Card, SectionHeader } from "../ui";

export default function LibraryHelpPanel() {
  return (
    <Card className="h-full">
      <SectionHeader title="使用说明" subtitle="如何管理自定义器件" icon={<FileSpreadsheet size={16} />} />
      <div className="space-y-3 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
        <p>
          <strong className="text-slate-800 dark:text-slate-200">内置数据：</strong>
          来自系统预置目录，只读。匹配引擎会自动将其纳入候选。
        </p>
        <p>
          <strong className="text-slate-800 dark:text-slate-200">自定义数据：</strong>
          通过表单或 CSV / Excel 批量导入。创建后立即可在各领域选型页面参与匹配。
        </p>
        <p>
          <strong className="text-slate-800 dark:text-slate-200">去重规则：</strong>
          导入时按「厂商 + 型号」去重。已存在条目会被跳过，不会覆盖。
        </p>
        <p>
          <strong className="text-slate-800 dark:text-slate-200">文件要求：</strong>
          文件名需包含 <code className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-700">lens</code> 或
          <code className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-700">detector</code> /
          <code className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-700">camera</code> 以便自动识别。
        </p>
      </div>
    </Card>
  );
}
