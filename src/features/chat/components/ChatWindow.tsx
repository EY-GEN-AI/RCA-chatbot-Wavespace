//The code is to display the dataframe correctly, 

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Mic, Send, Bot, Plus, MessageSquare, LogOut, ChevronLeft, ChevronRight, Download, Home, Sun, Moon, ArrowRight,List, FileText  } from 'lucide-react';
import { useAuth } from '../../auth/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { ChatService } from '../services/chatService';
import { Message, ChatSession } from '../types';
import UserAvatar from '../../../components/UserAvatar';
import Tooltip from '../../../components/Tooltip';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import PlanSummaryModal from '../../chat/components/PlanSummaryModal';

// NEW CODE: Import the Asddf modal
import Asddf from '../../../components/AskDF';

// import { Mic } from 'lucide-react';




interface ChatWindowProps {
  initialSession?: ChatSession;
}

export default function ChatWindow({ initialSession }: ChatWindowProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(initialSession || null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const { isListening, startListening, stopListening } = useSpeechRecognition();
  const [originalMessageId, setOriginalMessageId] = useState<string | null>(null);
  const [dfQuestions, setDfQuestions] = useState<Message[]>([]); // New state to store DF-related messages
  const [isPlanSummaryModalOpen, setIsPlanSummaryModalOpen] = useState(false);





  // NEW CODE: local states to control the asddf modal
  const [showDFModal, setShowDFModal] = useState(false);
  const [dfData, setDfData] = useState<any>(null);
  const [dfSummary, setDfSummary] = useState<string | undefined>(undefined);
  



  // const handleAskOnDF = async (question: string) => {
  //   if (!currentSession || !originalMessageId || !question.trim()) return;
  
  //   const userMessage: Message = {
  //     id: Date.now().toString(),
  //     text: question,
  //     sender: 'user',
  //     role: 'user',
  //     timestamp: new Date(),
  //     sessionId: currentSession.id,
  //   };
  
  //   setDfQuestions((prev) => [...prev, userMessage]);
  
  //   try {
  //     const response = await ChatService.askOnDF(
  //       currentSession.id,
  //       originalMessageId,
  //       question
  //     );
  //     setDfQuestions((prev) => [...prev, response]); // Add DF-related response to DF-specific messages
  //   } catch (error) {
  //     console.error('Failed to fetch response for DF question:', error);
  //   }
  // };

  const handlePlanSummary = () => {
    setIsPlanSummaryModalOpen(true);
  };
  const handlePlanSummaryResponse = (summaryResponse) => {
    if (!currentSession || !summaryResponse) return;

  
  
    // Create assistant message with the summary
    const assistantMessage = {
      id: Date.now().toString(),
      text: summaryResponse, // Use the summary string directly
      sender: 'assistant',
      role: 'assistant',
      timestamp: new Date(),
      sessionId: currentSession.id
    };
  
    // Add assistant message to chat
    // setCurrentSession(prev => ({
    //   ...prev!,
    //   messages: [...prev!.messages, assistantMessage],
    //   lastMessage: "Plan Summary Generated",
    //   timestamp: new Date()
    // }));
  
  
    // Update sessions list
    setSessions(prev => prev.map(session => 
      session.id === currentSession.id 
        ? { ...session, lastMessage: assistantMessage.text, timestamp: new Date() }
        : session
    ));
  };


  const handleAskOnDF = async (question: string) => {
    if (!currentSession || !originalMessageId || !question.trim()) return;
  
    const userMessage: Message = {
      id: Date.now().toString(),
      text: question,
      sender: 'user',
      role: 'user',
      timestamp: new Date(), // Use ISO format for consistency new Date(),
      sessionId: currentSession.id,
    };
  
    // Add the user question to DF-specific messages
    setDfQuestions((prev) => [...prev, userMessage]);
  
    try {
      const response = await ChatService.askOnDF(
        currentSession.id,
        originalMessageId,  // Pass the parent message ID
        question
      );
      // Append the response to DF-specific messages
      setDfQuestions((prev) => [...prev, response]);
    } catch (error) {
      console.error('Failed to fetch response for DF question:', error);
    }
  };
  
  

  const handleNextQuestionClick = (question: string) => {
    // Log the selected next question for debugging
    console.log('Selected next question:', question);
    
    // Populate the input with the selected question
    setInputMessage(question);
  };

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    
  }, []);


  // useEffect(() => {
  //   const fetchSessions = async () => {
  //       try {
  //           const history = await ChatService.getChatHistory();

  //           // Filter messages for each session
  //           const filteredHistory = history.map(session => ({
  //               ...session,
  //               messages: session.messages.filter((message: Message) => !message.df_parent)
  //           }));

  //           setSessions(filteredHistory);
  //           if (!currentSession && filteredHistory.length > 0) {
  //               setCurrentSession(filteredHistory[0]);
  //           } else if (!filteredHistory.length) {
  //               handleNewChat();
  //           }
  //       } catch (error) {
  //           console.error('Failed to fetch chat history:', error);
  //       }
  //   };

  //   fetchSessions();
  // }, [currentSession]);



  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const history = await ChatService.getChatHistory();
        setSessions(history); // Set filtered sessions to state
  
        if (!currentSession && history.length > 0) {
          setCurrentSession(history[0]);
        } else if (!history.length) {
          handleNewChat(); // Handle no existing chats
        }
      } catch (error) {
        console.error('Failed to fetch chat history:', error);
      }
    };
  
    fetchSessions();
  }, [currentSession]);
  


  useEffect(() => {
    scrollToBottom();
  }, [currentSession?.messages, scrollToBottom]);




  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    document.documentElement.classList.toggle('dark');
  };

  const handleNewChat = async () => {
    try {
      setIsLoading(true);
      const newSession = await ChatService.createNewChat();
      setSessions(prev => [newSession, ...prev]);
      setCurrentSession(newSession);
      setInputMessage('');
    } catch (error) {
      console.error('Failed to create new chat:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // const handlePlanSummary = async () => {
  //   try {
  //     setIsLoading(true);
  //     const planSummary = await ChatService.createPlanSummary;
      
      
  //   } catch (error) {
  //     console.error('Failed to Generate Plan Summary', error);
  //   } finally {
  //     setIsLoading(false);
  //   }
  // };

  const handleDeleteSession = async (sessionId: string) => {
    const confirmed = window.confirm('Are you sure you want to delete this chat?');
    if (!confirmed) return;
  
    try {
      await ChatService.deleteChatSession(sessionId);
      // Update the sessions state
      setSessions((prevSessions) => prevSessions.filter((session) => session.id !== sessionId));
  
      // Clear the current session if it's the one being deleted
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
      }
    } catch (error) {
      console.error('Error deleting chat session:', error);
      alert('Failed to delete the chat session. Please try again.');
    }
  };
  
  

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening((transcript) => setInputMessage(transcript));
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading || !currentSession) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputMessage.trim(),
      sender: 'user',
      role: 'user',
      timestamp: new Date(), // Use ISO format for consistency new Date(),
      sessionId: currentSession.id
    };

    setCurrentSession((prev: ChatSession | null) => {
      if (!prev) return null;
      return {
        ...prev,
        messages: [...prev.messages, userMessage]
      };
    });
    
    // setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      console.log('Sending message:', inputMessage.trim());
      
      const response = await ChatService.sendMessage(inputMessage.trim(), currentSession.id);
      console.log('Received response:', response);
      setCurrentSession((prev: ChatSession | null) => {
        if (!prev) return null;
        return {
          ...prev,
          messages: [...prev.messages, response],
          lastMessage: response.text,
          timestamp: new Date(), // Ensure a valid timestamp is present new Date()
        };
      });

      setSessions(prev => prev.map(session => 
        session.id === currentSession.id 
          ? { ...session, lastMessage: response.text, timestamp: new Date() }
          : session
      ));
    } catch (error) {
      console.error('Failed to send message:', error);
      setCurrentSession((prev: ChatSession | null) => {
        if (!prev) return null;
        return {
          ...prev,
          messages: [...prev.messages, {
            id: Date.now().toString(),
            text: 'Sorry, I encountered an error. Please try again.',
            sender: 'bot',
            role: 'assistant',
            timestamp: new Date(),
            sessionId: currentSession.id,
            
          }]
        };
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSessionSelect = async (session: ChatSession) => {
    try {
        setIsLoading(true);
        const messages = await ChatService.getSessionMessages(session.id);

        // Filter out DF-related messages
        const filteredMessages = messages.filter((message: Message) => !message.df_parent);

        setCurrentSession({ ...session, messages: filteredMessages });
    } catch (error) {
        console.error('Failed to load session:', error);
    } finally {
        setIsLoading(false);
    }
  };

  

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const filteredSessions = sessions.filter(session => 
    session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    session.lastMessage?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={`flex h-screen ${theme === 'dark' ? 'bg-dark-bg' : 'bg-light-bg'}`}>
      <div className={`${
        isSidebarOpen ? 'w-70' : 'w-20'
      } ${
        theme === 'dark' ? 'bg-dark-sidebar' : 'bg-light-sidebar'
      } border-r ${
        theme === 'dark' ? 'border-dark-border' : 'border-light-border'
      } transition-all duration-300 flex flex-col shadow-lg`}>
        <div className="p-4 space-y-2">
          <button
            onClick={handleNewChat}
            className="flex items-center justify-center w-full px-4 py-3 rounded-lg bg-primary text-secondary-dark hover:bg-primary-dark transition-all duration-300 transform hover:scale-105 shadow-light-glow hover:shadow-xl group"
          >
            {isSidebarOpen ? (
              <>
                <Plus className="w-5 h-5 mr-2" />
                <span>New Analysis</span>
              </>
            ) : (
              <Plus className="w-5 h-5" />
            )}
          </button>

          <button
            onClick={handlePlanSummary}
            className="flex items-center justify-center w-full px-4 py-3 rounded-lg bg-primary text-secondary-dark hover:bg-primary-dark transition-all duration-300 transform hover:scale-105 shadow-light-glow hover:shadow-xl group"
          >
            {isSidebarOpen ? (
              <>
                <FileText className="w-5 h-5 mr-2" />
                <span>Plan Summary</span>
              </>
            ) : (
              < FileText className="w-5 h-5" />
            )}
          </button>

          <button
            onClick={() => navigate('/')}
            className={`flex items-center justify-center w-full px-4 py-3 rounded-lg ${
              theme === 'dark' 
                ? 'bg-dark-hover text-primary hover:bg-dark-hover/80' 
                : 'bg-light-hover text-primary hover:bg-light-hover/80'
            } transition-all duration-300 transform hover:scale-105 shadow-md hover:shadow-lg group`}
          >
            {isSidebarOpen ? (
              <>
                <Home className="w-5 h-5 mr-2" />
                <span>Home</span>
              </>
            ) : (
              <Home className="w-5 h-5" />
            )}
          </button>

          {isSidebarOpen && (
            <input
              type="text"
              placeholder="Search chats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full px-3 py-2 rounded-lg ${
                theme === 'dark'
                  ? 'bg-dark-hover text-dark-text-primary placeholder-dark-text-secondary'
                  : 'bg-light-hover text-light-text-primary placeholder-light-text-secondary border border-light-border'
              } focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-300 shadow-inner`}
            />
          )}
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-2">
          {filteredSessions.map((session) => (
            <div
              key={session.id}
              className={`w-full flex items-center justify-between mb-2 p-3 rounded-lg hover:bg-gray-800 transition-all duration-300 transform hover:scale-105 ${
                currentSession?.id === session.id
                  ? theme === 'dark' ? 'bg-dark-hover' : 'bg-light-hover'
                  : ''
              }`}
            >
              {/* Session Clickable Area */}
              <button
                onClick={() => handleSessionSelect(session)}
                className="flex items-center flex-1 text-left"
              >
                <MessageSquare
                  className={`w-4 h-4 ${
                    currentSession?.id === session.id ? 'text-primary' : 'text-gray-400'
                  } group-hover:text-primary mr-2`}
                />
                {isSidebarOpen && (
                  <div className="overflow-hidden">
                    <p
                      className={`text-sm ${
                        theme === 'dark' ? 'text-dark-text-primary' : 'text-light-text-primary'
                      } truncate`}
                    >
                      {session.title || session.lastMessage}
                    </p>
                    <p
                      className={`text-xs ${
                        theme === 'dark' ? 'text-dark-text-secondary' : 'text-light-text-secondary'
                      }`}
                    >
                      {/* {new Date(session.timestamp).toLocaleDateString()} */}
                      {new Date(session.timestamp).toLocaleDateString([], {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                      })}
                      {/* {'   '}
                      {new Date(session.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true, // Ensures 12-hour format with am/pm
                      })} */}
                    </p>
                  </div>
                )}
              </button>

              {/* Delete Button */}
              <button
                onClick={() => handleDeleteSession(session.id)}
                className="text-red-500 hover:text-red-700 transition-all duration-300 transform hover:scale-105 ml-2"
                aria-label="Delete Chat"
              >
                ✕
              </button>
            </div>
          ))}
        </div>


        <div className={`p-4 border-t ${
          theme === 'dark' ? 'border-dark-border' : 'border-light-border'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <Tooltip content={`${user?.full_name} (${user?.email})`}>
              <div className="flex items-center space-x-2">
                <UserAvatar name={user?.full_name || ''} size="sm" />
                {isSidebarOpen && (
                  <span className={`text-sm ${
                    theme === 'dark' ? 'text-dark-text-primary' : 'text-light-text-primary'
                  }`}>
                    {user?.full_name}
                  </span>
                )}
              </div>
            </Tooltip>
            <button
              onClick={toggleTheme}
              className={`p-2 rounded-lg ${
                theme === 'dark'
                  ? 'hover:bg-dark-hover text-dark-text-secondary hover:text-dark-text-primary'
                  : 'hover:bg-light-hover text-light-text-secondary hover:text-light-text-primary'
              } transition-all duration-300 hover:scale-105`}
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center justify-center w-full px-4 py-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-all duration-300 transform hover:scale-105"
          >
            {isSidebarOpen ? (
              <>
                <LogOut className="w-5 h-5 mr-2" />
                <span>Logout</span>
              </>
            ) : (
              <LogOut className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      <div className="flex-1 flex flex-col max-w-full overflow-x-auto">
        <div className={`${
          theme === 'dark' 
            ? 'bg-dark-sidebar border-dark-border' 
            : 'bg-white border-light-border'
        } p-4 border-b flex items-center justify-between shadow-md`}>
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className={`p-2 rounded-lg ${
              theme === 'dark'
                ? 'hover:bg-dark-hover text-primary'
                : 'hover:bg-light-hover text-primary'
            } transition-all duration-300 hover:scale-105`}
          >
            {isSidebarOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
          </button>

          <div className="flex items-center space-x-3">
            <Bot className="w-8 h-8 text-primary animate-pulse-subtle" />
            <div>
              <h2 className={`text-xl font-semibold ${
                theme === 'dark' ? 'text-dark-text-primary' : 'text-light-text-primary'
              }`}>
                RCA/PQA Supply Chain Analysis
              </h2>
              <p className={`text-sm ${
                theme === 'dark' ? 'text-dark-text-secondary' : 'text-light-text-secondary'
              }`}>
                AI-powered Root Cause & Plan Quality Analysis
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button className={`flex items-center space-x-2 ${
              theme === 'dark' 
                ? 'text-dark-text-secondary hover:text-dark-text-primary' 
                : 'text-light-text-secondary hover:text-light-text-primary'
              } transition-all duration-300 hover:scale-105`}>
              <Download className="w-5 h-5" />
              <span>Export</span>
            </button>
          </div>
        </div>

  {/* ----------------------------------------------------------------------------------------------------------------         */}

        <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${
        theme === 'dark' ? 'bg-dark-bg' : 'bg-light-bg'
      }`}>
        {currentSession?.messages
        .filter((message: Message) => !message.df_parent) // Exclude DF-related messages
        .map((message: Message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 shadow-message hover:shadow-message-hover ${
                message.sender === 'user'
                  ? 'bg-primary text-secondary-dark'
                  : theme === 'dark'
                    ? 'bg-dark-sidebar text-dark-text-primary'
                    : 'bg-white text-light-text-primary border border-light-border'
              } transform transition-all duration-300 hover:scale-[1.02]`}
            >
              {isLoading && message.sender !== 'user' && !message.text && !message.table_data && !message.summary ? (
                // Spinner in assistant's message
                <div className="flex items-center space-x-2">
                  <div className="loading-spinner"></div>
                  <p className="text-gray-400">Please wait while Agent is compiling answers ...</p>
                </div>
              ) : (
                <>
                  {message.table_data ? (
                    <>
                      {/* Table Display */}
                      <div className="overflow-auto max-h-96 scrollbar">
                        <table className="table-auto border-collapse border border-gray-300 w-full text-sm ">
                          <thead className="bg-yellow-500 text-black sticky top-0">
                            <tr>
                              {message.table_data.columns.map((column, index) => (
                                <th
                                  key={index}
                                  className="border border-gray-300 px-4 py-2 bg-primary text-center text-black"
                                >
                                  {column}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {message.table_data.records.map((record, rowIndex) => (
                              <tr key={rowIndex}>
                                {message.table_data.columns.map((column, colIndex) => (
                                  <td
                                    key={colIndex}
                                    className="border border-yellow-300 px-4 py-2 text-left"
                                  >
                                    {record[column]}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>



                      {/* <button
                          onClick={() => {
                              setDfData(message.table_data);
                              setOriginalMessageId(message.id); // Capture the message ID
                              setShowDFModal(true);
                          }}
                          className="mt-2 px-3 py-1 bg-primary text-white rounded hover:bg-primary-dark"
                      >
                          Ask on DF?
                      </button> */}

                      {/* Ask on DF Button */}
                      <div className="flex justify-end mt-4">
                        <button
                          onClick={() => {
                            setDfData(message.table_data);
                            setOriginalMessageId(message.id); // Capture the message ID
                            setShowDFModal(true);
                          }}
                          className="bg-yellow-500 text-black px-6 py-2 rounded hover:bg-yellow-600 transition-all"
                        >
                          Ask on DF?
                        </button>
                      </div>







                      {/* Summary Display */}
                      {message.summary && (
                        <p className="mt-4 text-sm text-white whitespace-pre-wrap">
                          {message.summary.split(/(\*\*.*?\*\*|###.*|#####.*)/g).map((part, index) => {
                            if (part.startsWith('**') && part.endsWith('**')) {
                              return (
                                <strong key={index} className="font-bold">
                                  {part.slice(2, -2)}
                                </strong>
                              );
                            } else if (part.startsWith('###') && !part.startsWith('#####')) {
                              return (
                                <h3 key={index} className="text-lg font-semibold mt-2">
                                  {part.slice(3).trim()}
                                </h3>
                              );
                            } else if (part.startsWith('#####')) {
                              return (
                                <h5 key={index} className="text-sm font-medium mt-1">
                                  {part.slice(5).trim()}
                                </h5>
                              );
                            } else {
                              return <span key={index}>{part}</span>;
                            }
                          })}
                        </p>
                      )}


                      {/* <button
                          onClick={() => {
                              setDfData(message.table_data);
                              setOriginalMessageId(message.id); // Capture the message ID
                              setShowDFModal(true);
                          }}
                          className="mt-2 px-3 py-1 bg-primary text-white rounded hover:bg-primary-dark"
                      >
                          Ask on DF?
                      </button> */}









                    </>
                  ) : (
                    // Text Display
                    // <p className="whitespace-pre-wrap">{message.text}</p>
                    <div className="whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: message.text }} />

                  )}
                </>
              )}

              {message.next_question && message.next_question.length > 0 && (
                <div className="container mx-auto p-4 pt-8  text-white" >
                  <div className="text-sm font-semibold mb-1">Suggested Next Questions:</div>
                  {message.next_question.map((question, index) => (
                    <div
                      key={index}
                      onClick={() => handleNextQuestionClick(question)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center justify-between mb-1 ${
                        theme === 'dark'
                          ? 'bg-dark-hover text-dark-text-primary hover:bg-dark-hover/80'
                          : 'bg-light-hover text-light-text-primary hover:bg-light-hover/80'
                      } transition-all duration-300 group`}
                    >
                      {question}
                    </div>
                  ))}
                </div>
              )}

              {/* Timestamp */}
              {/* <span className={`text-xs ${
                message.sender === 'user'
                  ? 'opacity-75'
                  : theme === 'dark'
                    ? 'text-dark-text-secondary'
                    : 'text-light-text-secondary'
              } block mt-2`}>
                {new Date(message.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span> */}
              <span
                className={`text-xs ${
                  message.sender === 'user'
                    ? 'opacity-75'
                    : theme === 'dark'
                      ? 'text-dark-text-secondary'
                      : 'text-light-text-secondary'
                } block mt-2`}
              >
                {new Date(message.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>


            </div>
          </div>
        ))}

        {/* If assistant is still processing and there's no existing assistant message, show spinner */}
        {isLoading && !currentSession?.messages.some((message) => message.sender === 'assistant') && (
          <div className="flex justify-start">
            <div
              className={`max-w-[80%] rounded-lg p-4 shadow-message hover:shadow-message-hover ${
                theme === 'dark'
                  ? 'bg-dark-sidebar text-dark-text-primary'
                  : 'bg-white text-light-text-primary border border-light-border'
              } transform transition-all duration-300 hover:scale-[1.02]`}
            >
              <div className="flex items-center space-x-2">
                <div className="loading-spinner"></div>
                <p className="text-gray-400">Please wait while Agent is compiling answers ...</p>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className={`p-4 border-t ${
        theme === 'dark' 
          ? 'border-dark-border bg-dark-sidebar' 
          : 'border-light-border bg-white shadow-lg'
      }`}>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type your supply chain query..."
              className={`flex-1 rounded-lg px-4 py-3 ${
                theme === 'dark'
                  ? 'bg-dark-hover text-dark-text-primary placeholder-dark-text-secondary'
                  : 'bg-light-hover text-light-text-primary placeholder-light-text-secondary border border-light-border'
              } focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-300 shadow-inner`}
              disabled={isLoading}
            />

            {/* Microphone button */}
            <button
              onClick={toggleListening}
              className={`p-3 rounded-lg transition-colors transform hover:scale-105 ${
                isListening 
                  ? 'bg-red-500 text-white' 
                  : theme === 'dark'
                    ? 'bg-dark-hover text-dark-text-primary'
                    : 'bg-light-hover text-light-text-primary'
              } hover:opacity-80`}
            >
              <Mic className="w-5 h-5" />
            </button>

            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-primary text-secondary-dark p-3 rounded-lg hover:bg-primary-dark transition-all duration-300 transform hover:scale-105 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
      {/* NEW CODE: Render the Asddf modal outside the messages map */}
      {/* <Asddf
        open={showDFModal}
        onClose={() => setShowDFModal(false)}
        sessionId={currentSession?.id || ''}
        parentMessageId={originalMessageId || ''}
        tableData={dfData || { columns: [], records: [] }}
        existingDFMessages={dfQuestions || []}
      /> */}

        <Asddf
          open={showDFModal}
          onClose={() => setShowDFModal(false)}
          sessionId={currentSession?.id || ''}
          parentMessageId={originalMessageId || ''}
          tableData={dfData || { columns: [], records: [] }}
          existingDFMessages={dfQuestions || []} // Pass DF-specific messages
        />

        {/* <PlanSummaryModal 
          isOpen={isPlanSummaryModalOpen} 
          onClose={() => setIsPlanSummaryModalOpen(false)} 
          onSummaryReceived={handlePlanSummaryResponse}
        /> */}
        <PlanSummaryModal
          isOpen={isPlanSummaryModalOpen}
          onClose={() => setIsPlanSummaryModalOpen(false)}
          onSummaryReceived={handlePlanSummaryResponse}
        />




    </div>
  );
}