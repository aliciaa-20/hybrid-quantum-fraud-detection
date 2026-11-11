type Option = { value: string; label: string };
type Props = { options: Option[]; value: string; onChange: (v: string) => void; label: string };

/** A pill-shaped single-choice switch. */
export default function Segmented({ options, value, onChange, label }: Props) {
  return (
    <div className="segmented" role="group" aria-label={label}>
      {options.map((o) => (
        <button key={o.value} className={o.value === value ? "on" : ""} aria-pressed={o.value === value} onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}
