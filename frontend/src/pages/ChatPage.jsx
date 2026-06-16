import React, { useState, useRef, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Spinner, Accordion, Badge, Image } from 'react-bootstrap';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const ChatPage = () => {
  const parseAnswer = (text) => {
    // Search for suggestion pattern [GOI_Y: ... | ... | ...]
    const match = text.match(/\[GOI_Y:\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\]/);
    if (match) {
      const cleanText = text.replace(match[0], '').trim();
      const suggestions = [match[1].trim(), match[2].trim(), match[3].trim()];
      return { cleanText, suggestions };
    }
    return { cleanText: text, suggestions: [] };
  };

  const [messages, setMessages] = useState([
    { 
      id: 1, 
      type: 'bot', 
      text: 'Xin chào! Tôi là Trợ lý AI Tư vấn Tuyển sinh Đại học. Hệ thống hiện hỗ trợ tra cứu thông tin của 5 trường Đại học đối tác. Bạn muốn hỏi gì?' 
    }
  ]);
  const [sessionId, setSessionId] = useState(() => {
    let sid = localStorage.getItem('chat_sessionId');
    if (!sid) {
      sid = 'sess_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now();
      localStorage.setItem('chat_sessionId', sid);
    }
    return sid;
  });
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`http://localhost:8080/api/chat/history?sessionId=${sessionId}`);
        if (response.data && response.data.length > 0) {
          const loadedMessages = [];
          response.data.forEach((chat, index) => {
            loadedMessages.push({ id: `user_${index}`, type: 'user', text: chat.question });
            
            const { cleanText, suggestions } = parseAnswer(chat.answer);
            
            loadedMessages.push({ 
              id: `bot_${index}`, 
              type: 'bot', 
              text: cleanText, 
              suggestions: suggestions,
              historyId: chat.id, 
              isLiked: chat.isLiked, 
              feedback: chat.feedback 
            });
          });
          setMessages(loadedMessages);
        }
      } catch (error) {
        console.error("Lỗi tải lịch sử từ Database:", error);
      }
    };
    fetchHistory();
  }, [sessionId]);

  const handleSend = async (e, predefinedMessage = null) => {
    if (e) e.preventDefault();
    
    const userMessage = predefinedMessage || input.trim();
    if (!userMessage || isLoading) return;

    setInput('');
    setMessages(prev => [...prev, { id: Date.now(), type: 'user', text: userMessage }]);
    setIsLoading(true);

    // Context Window Injection: Append recent messages to build short-term memory
    let contextQuery = userMessage;
    if (messages.length >= 2) {
      const recentMessages = messages.slice(-2);
      let historyText = "";
      recentMessages.forEach(msg => {
        if (msg.type === 'user') historyText += `\nUser hỏi trước đó: ${msg.text}`;
        if (msg.type === 'bot') historyText += `\nAI đã trả lời: ${msg.text}`;
      });
      if (historyText) {
        contextQuery = `Lịch sử hội thoại ngắn gọn:${historyText}\n\nCâu hỏi hiện tại của User: ${userMessage}`;
      }
    }

    try {
      const response = await axios.post('http://localhost:8080/api/chat', {
        query: contextQuery,
        sessionId: sessionId
      });
      
      const { cleanText, suggestions } = parseAnswer(response.data.answer);
      
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        type: 'bot', 
        text: cleanText,
        suggestions: suggestions,
        historyId: response.data.historyId,
        isLiked: null,
        feedback: null
      }]);
    } catch (error) {
      console.error('Lỗi khi gọi API:', error);
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        type: 'bot', 
        text: 'Lỗi kết nối tới máy chủ AI. Vui lòng thử lại sau.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const submitFeedback = async (historyId, isLiked, feedbackText) => {
    try {
      await axios.post('http://localhost:8080/api/chat/feedback', {
        historyId: historyId,
        isLiked: isLiked,
        feedback: feedbackText
      });
      // Update state
      setMessages(prev => prev.map(msg => {
        if (msg.historyId === historyId) {
          return { ...msg, isLiked, feedback: feedbackText, showFeedbackForm: true };
        }
        return msg;
      }));
    } catch (error) {
      console.error('Lỗi khi gửi đánh giá:', error);
    }
  };

  const handleFeedbackSubmit = (e, historyId, isLiked) => {
    e.preventDefault();
    const text = e.target.elements.feedbackText.value;
    submitFeedback(historyId, isLiked, text);
  };

  const universities = [
    { name: "ĐH Khoa học và Công nghệ Hà Nội", nameEn: "USTH", logo: "/logos/usth.png" },
    { name: "Đại học Bách Khoa Hà Nội", nameEn: "HUST", logo: "/logos/hust.png" },
    { name: "Đại học Ngoại Thương", nameEn: "FTU", logo: "/logos/ftu.png" },
    { name: "Đại học Kinh tế Quốc dân", nameEn: "NEU", logo: "/logos/neu.png" },
    { name: "Đại học Công nghệ - ĐHQGHN", nameEn: "UET", logo: "/logos/uet.png" }
  ];

  const sampleTopics = [
    {
      title: "Chương trình Sau Đại học",
      icon: "bi-mortarboard",
      questions: [
        "Chỉ tiêu tuyển sinh Thạc sĩ ngành CNTT của USTH năm 2024?",
        "HUST có xét tuyển thẳng Tiến sĩ không?",
        "Học phí hệ cao học của NEU là bao nhiêu?"
      ]
    },
    {
      title: "Thông tin Ký túc xá & Học bổng",
      icon: "bi-building",
      questions: [
        "Điều kiện nội trú Ký túc xá của đại học Ngoại Thương?",
        "Tân sinh viên USTH được cấp học bổng tối đa bao nhiêu?",
        "Đại học Bách Khoa có học bổng tài năng không?"
      ]
    },
    {
      title: "Điểm chuẩn & Xét tuyển",
      icon: "bi-graph-up-arrow",
      questions: [
        "Ngành Khoa học máy tính của USTH lấy bao nhiêu điểm năm 2024?",
        "Đại học Ngoại Thương (FTU) có xét tuyển bằng IELTS không?",
        "Điểm chuẩn ngành Logistics của NEU năm ngoái?"
      ]
    },
    {
      title: "Thông tin Ngành học",
      icon: "bi-book",
      questions: [
        "Trường USTH đào tạo những ngành học mũi nhọn nào?",
        "Chương trình tiên tiến ngành AI của UET học những môn gì?"
      ]
    }
  ];

  return (
    <Container className="py-4">
      <Row>
        {/* Left column for guidance and sample questions */}
        <Col lg={4} className="mb-4">
          <Card className="shadow-sm border-0 mb-3">
            <Card.Header className="bg-white py-3 border-bottom-0">
              <h5 className="mb-0 text-primary">
                <i className="bi bi-bank me-2"></i>Đối tác Tuyển sinh
              </h5>
            </Card.Header>
            <Card.Body className="pt-0">
              <div className="d-flex flex-column gap-3">
                {universities.map((uni, index) => (
                  <div key={index} className="d-flex align-items-center p-2 border rounded shadow-sm bg-white">
                    <div style={{ width: '50px', height: '50px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f8f9fa', borderRadius: '8px', padding: '4px' }}>
                       <Image 
                         src={uni.logo} 
                         alt={uni.nameEn} 
                         style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }}
                         onError={(e) => {
                           e.target.onerror = null; 
                           e.target.src = 'https://placehold.co/50x50?text=' + uni.nameEn;
                         }} 
                       />
                    </div>
                    <div className="ms-3">
                      <div className="fw-bold text-dark" style={{ fontSize: '0.9rem' }}>{uni.nameEn}</div>
                      <div className="text-muted" style={{ fontSize: '0.75rem' }}>{uni.name}</div>
                    </div>
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>

          <Card className="shadow-sm border-0">
            <Card.Header className="bg-white py-3">
              <h5 className="mb-0 text-primary">
                <i className="bi bi-compass me-2"></i>Gợi ý câu hỏi
              </h5>
            </Card.Header>
            <Card.Body className="p-0" style={{ maxHeight: '300px', overflowY: 'auto' }}>
              <Accordion defaultActiveKey="0" flush>
                {sampleTopics.map((topic, index) => (
                  <Accordion.Item eventKey={index.toString()} key={index}>
                    <Accordion.Header>
                      <i className={`bi ${topic.icon} me-2 text-primary`}></i>
                      {topic.title}
                    </Accordion.Header>
                    <Accordion.Body className="p-3 bg-light">
                      <div className="d-flex flex-column gap-2">
                        {topic.questions.map((q, qIndex) => (
                          <Button 
                            key={qIndex}
                            variant="outline-primary" 
                            size="sm" 
                            className="text-start rounded-3 bg-white"
                            onClick={() => handleSend(null, q)}
                            disabled={isLoading}
                          >
                            <i className="bi bi-chat-left-dots me-2"></i>
                            {q}
                          </Button>
                        ))}
                      </div>
                    </Accordion.Body>
                  </Accordion.Item>
                ))}
              </Accordion>
            </Card.Body>
          </Card>
        </Col>

        {/* Right column for chat interface */}
        <Col lg={8} className="mb-4">
          <Card className="shadow-sm border-0 h-100">
            <Card.Header className="bg-primary text-white d-flex align-items-center py-3">
              <i className="bi bi-robot fs-4 me-2"></i>
              <div>
                <h5 className="mb-0">Trợ Lý AI Tuyển Sinh ĐH</h5>
                <small className="text-white-50">Sử dụng công nghệ RAG (Retrieval-Augmented Generation)</small>
              </div>
            </Card.Header>
            
            <Card.Body className="d-flex flex-column chat-scroll-area overflow-auto bg-light p-4" style={{ minHeight: '600px', maxHeight: '75vh' }}>
              {messages.map((msg) => (
                <div 
                  key={msg.id} 
                  className={`d-flex mb-3 ${msg.type === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
                >
                  {msg.type === 'bot' && (
                    <div className="me-2 text-primary">
                      <i className="bi bi-robot fs-3"></i>
                    </div>
                  )}
                  
                  <div 
                    className={`p-3 rounded-4 shadow-sm ${msg.type === 'user' ? 'bg-primary text-white' : 'bg-white text-dark border'}`}
                    style={{ 
                      maxWidth: '80%', 
                      borderTopLeftRadius: msg.type === 'bot' ? 0 : '', 
                      borderTopRightRadius: msg.type === 'user' ? 0 : '',
                      overflowWrap: 'break-word'
                    }}
                  >
                    {msg.type === 'bot' ? (
                      <div className="markdown-content">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                        
                        {msg.suggestions && msg.suggestions.length > 0 && (
                          <div className="mt-3 d-flex flex-wrap gap-2">
                            {msg.suggestions.map((sug, i) => (
                              <Button 
                                key={i} 
                                variant="outline-primary" 
                                size="sm" 
                                className="rounded-pill px-3 shadow-sm bg-white"
                                onClick={() => handleSend(null, sug)}
                                disabled={isLoading}
                              >
                                {sug}
                              </Button>
                            ))}
                          </div>
                        )}

                        {msg.historyId && (
                          <div className="mt-3 pt-2 border-top">
                            <div className="d-flex align-items-center gap-2 mb-2">
                              <small className="text-muted">Đánh giá câu trả lời:</small>
                              <Button 
                                variant={msg.isLiked === true ? "primary" : "outline-primary"} 
                                size="sm" 
                                className="rounded-circle d-flex align-items-center justify-content-center p-0" 
                                style={{width: '28px', height: '28px'}}
                                onClick={() => submitFeedback(msg.historyId, true, msg.feedback)}
                              >
                                <i className="bi bi-hand-thumbs-up"></i>
                              </Button>
                              <Button 
                                variant={msg.isLiked === false ? "danger" : "outline-danger"} 
                                size="sm" 
                                className="rounded-circle d-flex align-items-center justify-content-center p-0" 
                                style={{width: '28px', height: '28px'}}
                                onClick={() => submitFeedback(msg.historyId, false, msg.feedback)}
                              >
                                <i className="bi bi-hand-thumbs-down"></i>
                              </Button>
                            </div>
                            
                            {(msg.isLiked !== undefined && msg.isLiked !== null) && (
                              <Form onSubmit={(e) => handleFeedbackSubmit(e, msg.historyId, msg.isLiked)} className="d-flex gap-2 mt-2">
                                <Form.Control 
                                  size="sm" 
                                  name="feedbackText"
                                  placeholder="Góp ý thêm (tùy chọn)..." 
                                  defaultValue={msg.feedback || ''}
                                  className="bg-light"
                                />
                                <Button size="sm" type="submit" variant="secondary">Gửi</Button>
                              </Form>
                            )}
                          </div>
                        )}
                      </div>
                    ) : (
                      <span style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</span>
                    )}
                  </div>

                  {msg.type === 'user' && (
                    <div className="ms-2 text-secondary">
                      <i className="bi bi-person-circle fs-3"></i>
                    </div>
                  )}
                </div>
              ))}
              
              {isLoading && (
                <div className="d-flex mb-3 justify-content-start">
                  <div className="me-2 text-primary">
                    <i className="bi bi-robot fs-3"></i>
                  </div>
                  <div className="p-3 bg-white text-dark rounded-4 shadow-sm border typing-dots" style={{ borderTopLeftRadius: 0 }}>
                    <span></span><span></span><span></span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </Card.Body>
            
            <Card.Footer className="bg-white p-3 border-0 border-top">
              <Form onSubmit={(e) => handleSend(e, null)} className="d-flex gap-2">
                <Form.Control
                  type="text"
                  placeholder="Hỏi về điểm chuẩn, ngành học, học bổng..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  disabled={isLoading}
                  className="rounded-pill px-4 bg-light border-0 py-2"
                />
                <Button 
                  type="submit" 
                  variant="primary" 
                  className="rounded-circle d-flex justify-content-center align-items-center" 
                  style={{ width: '45px', height: '45px' }}
                  disabled={!input.trim() || isLoading}
                >
                  {isLoading ? <Spinner animation="border" size="sm" /> : <i className="bi bi-send-fill"></i>}
                </Button>
              </Form>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ChatPage;
