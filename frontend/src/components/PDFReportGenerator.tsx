import React, { useRef } from 'react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';

interface SimulationData {
  baseline: {
    revenue: number;
    costs: {
      labor: number;
      cogs: number;
      overhead: number;
    };
  };
  optimized: {
    costs: {
      labor: number;
      cogs: number;
      overhead: number;
    };
  };
  timeline_projections: Array<{
    month: number;
    savings: number;
    cumulative: number;
  }>;
  recommendations: Array<{
    title?: string;
    description: string;
    annual_savings?: number;
    savings?: number;
    implementation_cost?: number;
    cost?: number;
    priority: number;
    type?: string;
    three_year_roi?: number;
    five_year_roi?: number;
    payback_months?: number;
    three_year_savings?: number;
    five_year_savings?: number;
  }>;
  roi_metrics: {
    total_investment: number;
    payback_months: number;
    roi_percentage: number;
    annual_roi?: number;
    three_year_roi?: number;
    five_year_roi?: number;
    break_even_date?: string;
  };
  summary_metrics?: {
    total_savings: number;
    confidence_score: number;
  };
}

interface PDFReportGeneratorProps {
  data: SimulationData;
  companyName: string;
  onGenerate: () => void;
  buttonText?: string;
  buttonVariant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link' | 'destructive';
  buttonClassName?: string;
}

const PDFReportGenerator: React.FC<PDFReportGeneratorProps> = ({ 
  data, 
  companyName, 
  onGenerate, 
  buttonText = "Download Report",
  buttonVariant = "default",
  buttonClassName = ""
}) => {
  const reportRef = useRef<HTMLDivElement>(null);

  const generatePDF = async () => {
    if (!reportRef.current) return;

    onGenerate();

    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    let currentY = 20;

    // Helper function to add page break if needed
    const checkPageBreak = (requiredHeight: number) => {
      if (currentY + requiredHeight > pageHeight - 20) {
        pdf.addPage();
        currentY = 20;
      }
    };

    // Add SPAIK logo and title
    pdf.setFillColor(139, 92, 246); // Purple color
    pdf.rect(0, 0, pageWidth, 15, 'F');
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(16);
    pdf.text('SPAIK AI Business Assessment Report', 20, 10);

    // Company name and date
    pdf.setTextColor(0, 0, 0);
    pdf.setFontSize(14);
    pdf.text(`Company: ${companyName}`, 20, currentY);
    currentY += 10;
    pdf.setFontSize(10);
    pdf.text(`Generated: ${new Date().toLocaleDateString()}`, 20, currentY);
    currentY += 20;

    // Executive Summary
    pdf.setFontSize(16);
    pdf.setTextColor(139, 92, 246);
    pdf.text('Executive Summary', 20, currentY);
    currentY += 10;

    const totalCurrentCosts = data.baseline.costs.labor + data.baseline.costs.cogs + data.baseline.costs.overhead;
    const totalOptimizedCosts = data.optimized.costs.labor + data.optimized.costs.cogs + data.optimized.costs.overhead;
    const totalSavings = data.summary_metrics?.total_savings || (totalCurrentCosts - totalOptimizedCosts);

    pdf.setFontSize(10);
    pdf.setTextColor(0, 0, 0);
    const summaryText = [
      `Total Annual Savings: $${totalSavings.toLocaleString()}`,
      `3-Year ROI: ${(data.roi_metrics.three_year_roi || data.roi_metrics.roi_percentage || 0).toFixed(0)}%`,
      `Payback Period: ${data.roi_metrics.payback_months} months`,
      `Confidence Score: ${data.summary_metrics?.confidence_score || 87}%`,
      `Total Investment Required: $${data.roi_metrics.total_investment.toLocaleString()}`
    ];

    summaryText.forEach((text, index) => {
      pdf.text(text, 20, currentY + (index * 6));
    });
    currentY += 40;

    // Current vs Optimized Costs
    checkPageBreak(60);
    pdf.setFontSize(14);
    pdf.setTextColor(139, 92, 246);
    pdf.text('Current vs Optimized Cost Comparison', 20, currentY);
    currentY += 15;

    pdf.setFontSize(10);
    pdf.setTextColor(0, 0, 0);
    const costData = [
      ['Category', 'Current Costs', 'Optimized Costs', 'Savings'],
      ['Labor', `$${data.baseline.costs.labor.toLocaleString()}`, `$${data.optimized.costs.labor.toLocaleString()}`, `$${(data.baseline.costs.labor - data.optimized.costs.labor).toLocaleString()}`],
      ['COGS', `$${data.baseline.costs.cogs.toLocaleString()}`, `$${data.optimized.costs.cogs.toLocaleString()}`, `$${(data.baseline.costs.cogs - data.optimized.costs.cogs).toLocaleString()}`],
      ['Overhead', `$${data.baseline.costs.overhead.toLocaleString()}`, `$${data.optimized.costs.overhead.toLocaleString()}`, `$${(data.baseline.costs.overhead - data.optimized.costs.overhead).toLocaleString()}`],
      ['Total', `$${totalCurrentCosts.toLocaleString()}`, `$${totalOptimizedCosts.toLocaleString()}`, `$${totalSavings.toLocaleString()}`]
    ];

    costData.forEach((row, rowIndex) => {
      row.forEach((cell, colIndex) => {
        const x = 20 + (colIndex * 40);
        const y = currentY + (rowIndex * 8);
        if (rowIndex === 0) {
          pdf.setFont('helvetica', 'bold');
        } else {
          pdf.setFont('helvetica', 'normal');
        }
        pdf.text(cell, x, y);
      });
    });
    currentY += 50;

    // AI Recommendations
    checkPageBreak(80);
    pdf.setFontSize(14);
    pdf.setTextColor(139, 92, 246);
    pdf.text('AI Recommendations', 20, currentY);
    currentY += 15;

    data.recommendations
      .sort((a, b) => a.priority - b.priority)
      .forEach((rec, index) => {
        checkPageBreak(25);
        
        pdf.setFontSize(12);
        pdf.setTextColor(0, 0, 0);
        pdf.text(`${index + 1}. ${rec.title || rec.description}`, 20, currentY);
        currentY += 8;

        pdf.setFontSize(9);
        pdf.setTextColor(100, 100, 100);
        const descriptionLines = pdf.splitTextToSize(rec.description, 160);
        descriptionLines.forEach((line: string) => {
          pdf.text(line, 25, currentY);
          currentY += 4;
        });
        currentY += 2;

        pdf.setFontSize(8);
        pdf.setTextColor(0, 0, 0);
        pdf.text(`Annual Savings: $${(rec.annual_savings || rec.savings || 0).toLocaleString()}`, 25, currentY);
        pdf.text(`Investment: $${(rec.implementation_cost || rec.cost || 0).toLocaleString()}`, 100, currentY);
        currentY += 5;
        pdf.text(`3-Year ROI: ${(rec.three_year_roi || 0).toFixed(0)}%`, 25, currentY);
        pdf.text(`Payback: ${rec.payback_months || 12} months`, 100, currentY);
        currentY += 10;
      });

    // Implementation Roadmap
    checkPageBreak(50);
    pdf.setFontSize(14);
    pdf.setTextColor(139, 92, 246);
    pdf.text('Implementation Roadmap', 20, currentY);
    currentY += 15;

    const roadmapSteps = [
      'Phase 1 (Months 1-3): Assessment and Planning',
      '• Complete detailed operational analysis',
      '• Finalize technology selection and vendor partnerships',
      '• Develop implementation timeline and resource allocation',
      '',
      'Phase 2 (Months 4-6): Foundation Implementation',
      '• Deploy core AI systems and infrastructure',
      '• Begin staff training and change management',
      '• Implement pilot programs in selected areas',
      '',
      'Phase 3 (Months 7-12): Full Deployment',
      '• Roll out AI solutions across all identified areas',
      '• Monitor performance and optimize systems',
      '• Achieve full operational efficiency gains'
    ];

    pdf.setFontSize(10);
    pdf.setTextColor(0, 0, 0);
    roadmapSteps.forEach((step) => {
      checkPageBreak(6);
      pdf.text(step, 20, currentY);
      currentY += 5;
    });
    currentY += 10;

    // About SPAIK
    checkPageBreak(40);
    pdf.setFontSize(14);
    pdf.setTextColor(139, 92, 246);
    pdf.text('About SPAIK', 20, currentY);
    currentY += 15;

    pdf.setFontSize(10);
    pdf.setTextColor(0, 0, 0);
    const aboutText = `SPAIK is your AI-powered business transformation partner. We specialize in helping SME manufacturers implement AI solutions that drive real cost savings and operational efficiency. Our team of experts can guide you through the entire implementation process, from strategy to deployment. Contact us at info@spaik.io to start your AI transformation journey.`;
    
    const aboutLines = pdf.splitTextToSize(aboutText, 160);
    aboutLines.forEach((line: string) => {
      checkPageBreak(5);
      pdf.text(line, 20, currentY);
      currentY += 5;
    });

    // Add page numbers
    const pageCount = pdf.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      pdf.setFontSize(8);
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Page ${i} of ${pageCount}`, pageWidth - 30, pageHeight - 10);
    }

    // Generate charts as images and add to PDF
    try {
      const chartElements = reportRef.current.querySelectorAll('.pdf-chart');
      if (chartElements.length > 0) {
        pdf.addPage();
        currentY = 20;
        
        pdf.setFontSize(14);
        pdf.setTextColor(139, 92, 246);
        pdf.text('Performance Charts', 20, currentY);
        currentY += 20;

        for (let i = 0; i < chartElements.length; i++) {
          const element = chartElements[i] as HTMLElement;
          const canvas = await html2canvas(element, {
            scale: 2,
            backgroundColor: '#ffffff'
          });
          
          const imgData = canvas.toDataURL('image/png');
          const imgWidth = 160;
          const imgHeight = (canvas.height * imgWidth) / canvas.width;
          
          checkPageBreak(imgHeight + 10);
          pdf.addImage(imgData, 'PNG', 20, currentY, imgWidth, imgHeight);
          currentY += imgHeight + 15;
        }
      }
    } catch (error) {
      console.error('Error generating charts:', error);
    }

    // Save the PDF
    const filename = `SPAIK_AI_Assessment_${companyName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
    pdf.save(filename);
  };

  // Prepare chart data
  const totalCurrentCosts = data.baseline.costs.labor + data.baseline.costs.cogs + data.baseline.costs.overhead;
  const totalOptimizedCosts = data.optimized.costs.labor + data.optimized.costs.cogs + data.optimized.costs.overhead;

  const costComparisonData = [
    {
      name: 'Current Costs',
      labor: data.baseline.costs.labor,
      cogs: data.baseline.costs.cogs,
      overhead: data.baseline.costs.overhead,
    },
    {
      name: 'Optimized Costs',
      labor: data.optimized.costs.labor,
      cogs: data.optimized.costs.cogs,
      overhead: data.optimized.costs.overhead,
    },
  ];

  const pieData = [
    { name: 'Labor', value: data.optimized.costs.labor, color: '#8B5CF6' },
    { name: 'COGS', value: data.optimized.costs.cogs, color: '#06B6D4' },
    { name: 'Overhead', value: data.optimized.costs.overhead, color: '#10B981' },
  ].filter(item => item.value > 0);

  return (
    <div>
      <button 
        onClick={generatePDF}
        className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
          buttonVariant === 'outline' 
            ? `border ${buttonClassName || 'border-purple-600 text-purple-600 hover:bg-purple-50'}`
            : `bg-purple-600 text-white hover:bg-purple-700 ${buttonClassName}`
        }`}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        {buttonText}
      </button>
      
      {/* Hidden charts for PDF generation */}
      <div ref={reportRef} style={{ position: 'absolute', left: '-9999px', top: '-9999px' }}>
        <div className="pdf-chart" style={{ width: '800px', height: '400px', backgroundColor: 'white' }}>
          <h3 style={{ marginBottom: '20px', textAlign: 'center' }}>Cost Comparison</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={costComparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `$${Number(value).toLocaleString()}`} />
              <Bar dataKey="labor" fill="#8B5CF6" name="Labor" />
              <Bar dataKey="cogs" fill="#06B6D4" name="COGS" />
              <Bar dataKey="overhead" fill="#10B981" name="Overhead" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="pdf-chart" style={{ width: '800px', height: '400px', backgroundColor: 'white' }}>
          <h3 style={{ marginBottom: '20px', textAlign: 'center' }}>Cumulative Savings Projection</h3>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.timeline_projections}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Cumulative Savings']} />
              <Line 
                type="monotone" 
                dataKey="cumulative" 
                stroke="#8B5CF6" 
                strokeWidth={3}
                dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="pdf-chart" style={{ width: '800px', height: '400px', backgroundColor: 'white' }}>
          <h3 style={{ marginBottom: '20px', textAlign: 'center' }}>Optimized Cost Breakdown</h3>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={120}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `$${Number(value).toLocaleString()}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default PDFReportGenerator;