import { StoryDetails , Episode} from "@/types/story";
import { jsPDF } from "jspdf";

export const generatePDF = (story: StoryDetails) => {
  const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a5" });
  const margin = 20;
  const pageWidth = doc.internal.pageSize.width;
  const pageHeight = doc.internal.pageSize.height;
  const contentWidth = pageWidth - margin * 2;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(24);
  const titleLines = doc.splitTextToSize(story.title, contentWidth);
  const titleY = pageHeight / 2 - (titleLines.length * 10) / 2;
  titleLines.forEach((line: string, index: number) =>
    doc.text(line, pageWidth / 2, titleY + index * 10, { align: "center" }),
  );

  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);
  doc.text(
    "by: shakescript AI",
    pageWidth / 2,
    titleY + titleLines.length * 10 + 10,
    { align: "center" },
  );
  doc.addPage();

  doc.setFont("times", "normal");
  doc.setFontSize(12);

  story.episodes.forEach((ep:Episode, idx) => {
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text(
      `Chapter ${ep.episode_number}: ${ep.episode_title}`,
      margin,
      margin + 10,
    );

    doc.setFont("times", "normal");
    doc.setFontSize(12);
    const lines = doc.splitTextToSize(ep.episode_content, contentWidth);
    let y = margin + 20;
    lines.forEach((line: string) => {
      if (y > pageHeight - margin) {
        doc.addPage();
        y = margin + 10;
      }
      doc.text(line, margin, y);
      y += 7;
    });

    if (idx < story.episodes.length - 1) doc.addPage();
  });

  const totalPages = doc.internal.pages.length - 1;
  for (let i = 2; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.text(String(i), pageWidth - margin, pageHeight - margin);
  }

  doc.save(`${story.title.toLowerCase().replace(/\s+/g, "-")}.pdf`);
};
