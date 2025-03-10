import React, { useState, useEffect } from 'react';
import { X, Loader2 } from 'lucide-react';
import { ChatService } from '../services/chatService';

const RCAReportModal = ({ isOpen, onClose }) => {
  const [selectedModule, setSelectedModule] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [reportLink, setReportLink] = useState('');
  const [showLoader, setShowLoader] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setSelectedModule('');
      setIsLoading(false);
      setReportLink('');
      setShowLoader(false);
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    if (!selectedModule) return;
    
    setIsLoading(true);
    setShowLoader(true);
    
    try {
      const response = await ChatService.createRCAModuleSummary(selectedModule);
      
      setTimeout(() => {
        setReportLink(response);
        setShowLoader(false);
      }, 5000);

    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate report');
      setShowLoader(false);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-[680px] max-w-[95%] h-[600px] max-h-[95vh] bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700 shrink-0">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            Generate RCA Report
          </h2>
          <button
            onClick={onClose}
            className="text-red-500 hover:text-red-600 p-1.5 rounded-full"
          >
            <X size={18} />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 p-4 overflow-y-auto relative">
          {/* Module Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2 dark:text-gray-300">
              Select Module
            </label>
            <select
              value={selectedModule}
              onChange={(e) => setSelectedModule(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 dark:text-gray-200"
            >
              <option value="">Choose a module</option>
              <option value="ESP">ESP</option>
              <option value="DP">DP</option>
            </select>
          </div>

          {/* Selected Configuration */}
          {selectedModule && (
            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex justify-between items-center">
                <span className="text-yellow-500 font-medium">Selected Module:</span>
                <span className="font-semibold text-gray-800 dark:text-gray-200">
                  {selectedModule}
                </span>
              </div>
            </div>
          )}

          {/* Loading State */}
          {(isLoading || showLoader) && (
            <div className="absolute inset-0 bg-white dark:bg-gray-800 bg-opacity-90 dark:bg-opacity-90 flex flex-col items-center justify-center">
              <Loader2 className="animate-spin text-yellow-500 mb-4" size={48} />
              <p className="text-gray-800 dark:text-gray-200 text-center">
                {isLoading ? 'Processing request...' : 'Generating report...'}
              </p>
            </div>
          )}

          {/* Report Results */}
          {reportLink && (
            <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div 
                className="text-sm text-white dark:text-gray-300"
                dangerouslySetInnerHTML={{ __html: reportLink }}
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 p-4 border-t border-gray-200 dark:border-gray-700 shrink-0">
          <button
            onClick={handleSubmit}
            disabled={isLoading || !selectedModule || showLoader}
            className="px-4 py-2.5 bg-yellow-500 text-black rounded-lg hover:bg-yellow-600 disabled:opacity-50 transition-all"
            style={{ marginTop: '-12px' }} // Pull button up slightly
          >
            {isLoading ? 'Processing...' : 'Run Agent'}
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2.5 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            style={{ marginTop: '-12px' }} // Match button alignment
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default RCAReportModal;