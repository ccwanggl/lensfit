import { useState } from "react";
import { Bookmark } from "lucide-react";
import { Button } from "./ui";
import SaveToProjectDialog from "./SaveToProjectDialog";

interface SaveToProjectButtonProps {
  lensId: number | null;
  detectorId: number | null;
  lensModel: string;
  detectorModel: string;
  disabled?: boolean;
}

export default function SaveToProjectButton({
  lensId,
  detectorId,
  lensModel,
  detectorModel,
  disabled = false,
}: SaveToProjectButtonProps) {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        leftIcon={<Bookmark size={14} />}
        onClick={() => setShowModal(true)}
        disabled={disabled}
      >
        保存
      </Button>

      <SaveToProjectDialog
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        lensId={lensId ?? undefined}
        detectorId={detectorId ?? undefined}
        defaultName={`${lensModel} + ${detectorModel}`}
      />
    </>
  );
}
