
import React, { useState, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Upload, FileText, CheckCircle, XCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { API_BASE_URL } from '@/lib/api';

interface FileUploadProps {
  companyId: string;
  onUploadSuccess: (data: any) => void;
}

interface UploadedFile {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  data?: any;
}

const FileUpload: React.FC<FileUploadProps> = ({ companyId, onUploadSuccess }) => {
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files?.[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileUpload = async (file: File) => {
    const allowedTypes = ['.xlsx', '.csv', '.pdf'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      toast({
        title: "Invalid file type",
        description: "Please upload .xlsx, .csv, or .pdf files only",
        variant: "destructive"
      });
      return;
    }

    const uploadFile: UploadedFile = {
      file,
      progress: 0,
      status: 'uploading'
    };
    
    setUploadedFile(uploadFile);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/companies/${companyId}/upload-pl`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      
      setUploadedFile(prev => prev ? {
        ...prev,
        progress: 100,
        status: 'success',
        data: data.data
      } : null);

      toast({
        title: "Upload successful",
        description: "P&L statement processed successfully"
      });

      onUploadSuccess(data.data);
    } catch (error) {
      setUploadedFile(prev => prev ? {
        ...prev,
        status: 'error'
      } : null);

      toast({
        title: "Upload failed",
        description: "Failed to process your P&L statement. Please try again.",
        variant: "destructive"
      });
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card className="professional-card">
      <CardHeader>
        <CardTitle className="professional-heading">Upload P&L Statement</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive ? 'border-purple-500 bg-purple-50' : 'border-gray-300'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.csv,.pdf"
            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
            className="hidden"
          />
          
          {!uploadedFile ? (
            <>
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-lg professional-text mb-2">
                Drag and drop your P&L statement here
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Accepts .xlsx, .csv, and .pdf files
              </p>
              <Button
                onClick={() => fileInputRef.current?.click()}
                className="professional-button"
              >
                Choose File
              </Button>
            </>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-3">
                <FileText className="h-8 w-8 text-purple-600" />
                <div className="text-left">
                  <p className="font-medium text-gray-900">{uploadedFile.file.name}</p>
                  <p className="text-sm text-gray-500">{formatFileSize(uploadedFile.file.size)}</p>
                </div>
                {uploadedFile.status === 'success' && (
                  <CheckCircle className="h-6 w-6 text-green-500" />
                )}
                {uploadedFile.status === 'error' && (
                  <XCircle className="h-6 w-6 text-red-500" />
                )}
              </div>
              
              {uploadedFile.status === 'uploading' && (
                <Progress value={uploadedFile.progress} className="w-full" />
              )}
              
              {uploadedFile.status === 'success' && uploadedFile.data && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
                  <h4 className="font-semibold text-green-800 mb-2">Extracted P&L Summary:</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Revenue:</span> ${uploadedFile.data.revenue?.toLocaleString() || 'N/A'}
                    </div>
                    <div>
                      <span className="font-medium">COGS:</span> ${uploadedFile.data.cogs?.toLocaleString() || 'N/A'}
                    </div>
                    <div>
                      <span className="font-medium">Labor Costs:</span> ${uploadedFile.data.labor_costs?.toLocaleString() || 'N/A'}
                    </div>
                    <div>
                      <span className="font-medium">Overhead:</span> ${uploadedFile.data.overhead?.toLocaleString() || 'N/A'}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default FileUpload;
