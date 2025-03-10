import React, { useState } from 'react';
import { X, Download } from 'lucide-react';
import { ChatService } from '../services/chatService';

const PlanSummaryModal = ({ isOpen, onClose, onSummaryReceived }) => {
  const [selectedModule, setSelectedModule] = useState('');
  const [selectedReports, setSelectedReports] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [planSummaryData, setPlanSummaryData] = useState('');
  const [showResults, setShowResults] = useState(false);

  const espReports = [
    { value: 'MONTHLY_MAX_PROFIT', label: 'Monthly Max Profit' },
    { value: 'MONTHLY_DEM_SAT', label: 'Monthly DemSat' },
    { value: 'MONTHLY_BASE', label: 'Monthly Base' }
  ];

  const handleModuleChange = (e) => {
    setSelectedModule(e.target.value);
    setSelectedReports([]);
    setShowResults(false);
    setPlanSummaryData('');
  };

  const handleReportChange = (value) => {
    setSelectedReports(prev => 
      prev.includes(value) 
        ? prev.filter(item => item !== value) 
        : [...prev, value]
    );
    setShowResults(false);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const moduleFiles = {
        module: selectedModule,
        filename: selectedReports // Ensure these values match the backend's expected format
      };
      console.log("Module files :",moduleFiles)
      const response = await ChatService.createPlanSummary(moduleFiles);
      const summaryText = response?.summary || 'No data received';
      setPlanSummaryData(summaryText);
      onSummaryReceived(summaryText);
      setShowResults(true);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate summary');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (!planSummaryData) return;

    const date = new Date().toISOString().split('T')[0];
    const filename = `${selectedModule}_${date}_${selectedReports.join('-')}.txt`;
    
    const blob = new Blob([planSummaryData], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
  };



  const formatMarkdown = (text) => {
    if (!text) return [];
    
    const components = [];
    const lines = text.split('\n');
    const listItemRegex = /^(\s*)(\d+\.|\-|\*)\s+/;
    let currentContent = [];
    let tableContent = [];
    let inTable = false;
    let inList = false;
    let listItems = [];
  
    lines.forEach((line, index) => {



      if (listItemRegex.test(line)) {
        if (!inList) {
          inList = true;
          // Flush previous content
          if (currentContent.length > 0) {
            components.push({
              type: 'paragraph',
              content: currentContent.join('\n'),
              key: `para-list-${index}`
            });
            currentContent = [];
          }
        }
        // Split line into multiple list items if they're concatenated
        const items = line.split(/(\d+\.\s|\-\s|\*\s)/g)
          .filter(item => item && !listItemRegex.test(item));
        
        listItems.push(...items.filter(item => item.trim()));
        return;
      }



      // Handle headings (remove # symbols)
      if (line.startsWith('#')) {
        // Flush previous content
        if (currentContent.length > 0) {
          components.push({
            type: 'paragraph',
            content: currentContent.join('\n'),
            key: `para-${index}`
          });
          currentContent = [];
        }
        
        const headingContent = line.replace(/^#+\s*/, '');
        const headingLevel = Math.min(line.match(/^#+/)[0].length, 4); // Limit to h4 max
        components.push({
          type: `h${headingLevel}`,
          content: headingContent,
          key: `heading-${index}`
        });
        return;
      }
  
      // Handle tables
      if (line.trim().startsWith('|')) {
        if (!inTable) {
          // Flush previous content
          if (currentContent.length > 0) {
            components.push({
              type: 'paragraph',
              content: currentContent.join('\n'),
              key: `para-table-${index}`
            });
            currentContent = [];
          }
          inTable = true;
        }
        tableContent.push(line);
        return;
      } else if (inTable) {
        components.push({
          type: 'table',
          content: tableContent,
          key: `table-${index}`
        });
        tableContent = [];
        inTable = false;
      }
  
      // Handle lists
      if (/^\s*[-*]/.test(line)) {
        if (!inList) {
          inList = true;
          // Flush previous content
          if (currentContent.length > 0) {
            components.push({
              type: 'paragraph',
              content: currentContent.join('\n'),
              key: `para-list-${index}`
            });
            currentContent = [];
          }
        }
        listItems.push(line.trim());
        return;
      } else if (inList) {
        components.push({
          type: 'ul',
          content: listItems,
          key: `list-${index}`
        });
        listItems = [];
        inList = false;
      }
  
      // Handle regular paragraphs
      if (line.trim() === '' && currentContent.length > 0) {
        components.push({
          type: 'paragraph',
          content: currentContent.join('\n'),
          key: `para-${index}`
        });
        currentContent = [];
      } else if (line.trim() !== '') {
        currentContent.push(line);
      }
    });
  
    // Flush remaining content
    if (currentContent.length > 0) {
      components.push({
        type: 'paragraph',
        content: currentContent.join('\n'),
        key: `para-end`
      });
    }
    if (tableContent.length > 0) {
      components.push({
        type: 'table',
        content: tableContent,
        key: `table-end`
      });
    }
    if (listItems.length > 0) {
      components.push({
        type: 'ul',
        content: listItems,
        key: `list-end`
      });
    }
  
    return components;
  };

  // Function to render a table from markdown table rows
  const renderTable = (tableRows) => {
    if (!tableRows || tableRows.length < 2) return null;
    
    const headerRow = tableRows[0];
    const headers = headerRow
      .split('|')
      .filter(cell => cell.trim() !== '')
      .map(cell => cell.trim());
    
    const dataRows = tableRows.slice(2).map(row => 
      row
        .split('|')
        .filter(cell => cell.trim() !== '')
        .map(cell => cell.trim())
    );
    
    return (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full border-collapse border border-yellow-500">
          <thead className="bg-yellow-500">
            <tr>
              {headers.map((header, index) => (
                <th 
                  key={index} 
                  className="px-4 py-2 border border-gray-600 text-left font-semibold text-gray-600"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {dataRows.map((row, rowIndex) => (
              <tr 
                key={rowIndex} 
                className="hover:transition-colors"
              >
                {row.map((cell, cellIndex) => (
                  <td 
                    key={cellIndex} 
                    className="px-4 py-2 border border-gray-500  text-white"
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderList = (listItems, isOrdered) => {
    const ListTag = isOrdered ? 'ol' : 'ul';
    return (
      <ListTag className={`${isOrdered ? 'list-decimal' : 'list-disc'} pl-5 my-3 space-y-2`}>
        {listItems.map((item, index) => {
          // Split concatenated items
          const cleanedItem = item.replace(/(\d+\.)(\S)/g, '$1 $2')
                                 .replace(/(\*|\-)(\S)/g, '$1 $2');
          
          return (
            <li key={index} className="mb-1.5 text-white">
              {processTextFormatting(cleanedItem)}
            </li>
          );
        })}
      </ListTag>
    );
  };

  const processTextFormatting = (text) => {
    // Handle bold (**text**)
    let processedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Handle italic (*text*)
    processedText = processedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Handle bold text in headings and lists
    processedText = processedText.replace(/(^|\s)(\S.*?\S)(\s|$)/g, (match) => {
      return match.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    });
  
    return <span dangerouslySetInnerHTML={{ __html: processedText }} />;
  };


  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="relative w-[91%] h-[91%] bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg overflow-hidden">
        {/* Close Button */}
        <button
          onClick={() => {
            setSelectedModule('');
            setSelectedReports([]);
            setShowResults(false);
            onClose();
          }}
          className="absolute top-4 right-4 bg-red-500 text-white p-1.5 rounded-full hover:bg-red-600 z-50"
        >
          <X size={20} />
        </button>

        {/* Header */}
        <div className="flex items-center justify-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            {showResults ? 'Plan Summary Results' : 'Generate Plan Summary'}
          </h2>
        </div>

        {/* Content Container */}
        <div className="h-[85%] flex flex-col">
          {/* Form/Results Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {!showResults ? (
              <div className="flex gap-6 h-full">
                {/* Left Side - Selected Items */}
                <div className="w-1/3 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
                  <h3 className="text-lg font-medium mb-4">Selected Configuration</h3>
                  {selectedModule && (
                    <div className="mb-4">
                      <strong className="text-yellow-500">Module:</strong> {selectedModule}
                    </div>
                  )}
                  {selectedReports.length > 0 && (
                    <div>
                      <strong className="text-yellow-500">Reports:</strong>
                      <ul className="list-disc pl-4 space-y-1">
                        {selectedReports.map(report => (
                          <li key={report} className="text-gray-700 dark:text-gray-300">{report}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Right Side - Selection Controls */}
                <div className="w-2/3">
                  {/* Module Selection */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium mb-2 dark:text-gray-300">
                      Select Module
                    </label>
                    <select
                      value={selectedModule}
                      onChange={handleModuleChange}
                      className="w-full px-4 py-3 border rounded-lg bg-white dark:bg-gray-700 dark:text-gray-200"
                    >
                      <option value="">Choose a module</option>
                      <option value="ESP">ESP</option>
                      <option value="DP">DP</option>
                    </select>
                  </div>

                  {/* Report Selection */}
                  {selectedModule === 'ESP' && (        
                    <div className="mb-6">
                      <label className="block text-sm font-medium mb-2 dark:text-gray-300">
                        Select Reports
                      </label>
                      <div className="space-y-2">
                        {espReports.map(report => (
                          <label key={report.value} className="flex items-center">
                            <input
                              type="checkbox"
                              checked={selectedReports.includes(report.value)}
                              onChange={() => handleReportChange(report.value)}
                              className="rounded border-gray-300 text-yellow-500 focus:ring-yellow-500"
                            />
                            <span className="ml-3 text-gray-700 dark:text-gray-300">{report.label}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div>
                <div className="space-y-6">
                  {/* Selection Summary */}
                  <div className="bg-white dark:bg-gray-600 p-4 rounded-lg shadow-sm">
                    <div className="flex justify-between items-center mb-3">
                      <div className="text-yellow-500 font-medium">Selected Module:</div>
                      <div className="font-semibold text-gray-800 dark:text-gray-200">{selectedModule}</div>
                    </div>
                    <div className="flex justify-between items-center">
                      <div className="text-yellow-500 font-medium">Selected Reports:</div>
                      <div className="text-gray-700 dark:text-gray-300">{selectedReports.join(', ')}</div>
                    </div>
                  </div>

                  {/* Summary Content with Custom Rendering */}
                  <div className="bg-white dark:bg-gray-600 p-6 rounded-lg shadow-sm overflow-y-auto max-h-[60vh]">
                    {planSummaryData ? (
                      <div className="markdown-content">
                        {formatMarkdown(planSummaryData).map((component) => {
                          switch (component.type) {
                            case 'h1':
                              return (
                                <h1 key={component.key} className="text-3xl font-bold text-yellow-600 mb-4 mt-6">
                                  {processTextFormatting(component.content)}
                                </h1>
                              );
                            case 'h2':
                              return (
                                <h2 key={component.key} className="text-3xl font-semibold text-yellow-600 mb-3 mt-5">
                                  {processTextFormatting(component.content)}
                                </h2>
                              );
                            case 'h3':
                              return (
                                <h3 key={component.key} className="text-lg font-medium text-yellow-500 mb-2 mt-4">
                                  {processTextFormatting(component.content)}
                                </h3>
                              );
                            case 'h4':
                              return (
                                <h4 key={component.key} className="text-lg font-medium text-white-600 dark:text-yellow-500 mb-2 mt-3">
                                  {processTextFormatting(component.content)}
                                </h4>
                              );
                            case 'paragraph':
                              return (
                                <p key={component.key} className="mb-3 text-white dark:text-white">
                                  {processTextFormatting(component.content)}
                                </p>
                              );
                            case 'table':
                              return (
                                <div key={component.key}>
                                  {renderTable(component.content)}
                                </div>
                              );
                            case 'ul':
                              return (
                                <div key={component.key}>
                                  {renderList(component.content, false)}
                                </div>
                              );
                            case 'ol':
                              return (
                                <div key={component.key}>
                                  {renderList(component.content, true)}
                                </div>
                              );
                            default:
                              return null;
                          }
                        })}
                      </div>
                    ) : (
                      <p className="text-gray-500">No data available</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-4 p-4 bg-gray-50 dark:bg-gray-700">
            {!showResults ? (
              <button
                onClick={handleSubmit}
                disabled={isLoading || !selectedModule}
                className="px-6 py-3 bg-yellow-500 text-black rounded-lg hover:bg-yellow-600 disabled:opacity-50 transition-all"
              >
                {isLoading ? 'Processing...' : 'Run Agent'}
              </button>
            ) : (
              <>
                <button
                  onClick={() => setShowResults(false)}
                  className="px-6 py-2 bg-gray-200 text-gray-800 dark:bg-gray-600 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
                >
                  Back to Form
                </button>
                
                <button
                  onClick={handleDownload}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  <Download size={16} className="mr-2 inline" /> Download
                </button>
                
                <button
                  onClick={() => {
                    setSelectedModule('');
                    setSelectedReports([]);
                    setShowResults(false);
                    onClose();
                  }}
                  className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                >
                  Close
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanSummaryModal;