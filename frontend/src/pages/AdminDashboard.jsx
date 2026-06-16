import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Alert, Spinner, Tabs, Tab, Table, Badge } from 'react-bootstrap';
import axios from 'axios';

const AdminDashboard = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle');
  const [message, setMessage] = useState('');
  
  // States for new features
  const [stats, setStats] = useState({ totalUploads: 0, totalChats: 0, totalLikes: 0, totalDislikes: 0 });
  const [uploadHistory, setUploadHistory] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('upload');

  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const token = localStorage.getItem('admin_token');
    if (!token) return;
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [statsRes, uploadsRes, chatsRes] = await Promise.all([
        axios.get('http://localhost:8080/api/admin/stats', { headers }),
        axios.get('http://localhost:8080/api/admin/uploads', { headers }),
        axios.get('http://localhost:8080/api/admin/chats', { headers })
      ]);
      setStats(statsRes.data);
      setUploadHistory(uploadsRes.data);
      setChatHistory(chatsRes.data);
    } catch (error) {
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        handleLogout();
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    navigate('/admin/login');
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf' && selectedFile.type !== 'text/plain' && !selectedFile.name.endsWith('.docx')) {
        setStatus('error');
        setMessage('Chỉ hỗ trợ tải lên file PDF, DOCX hoặc TXT!');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setStatus('idle');
      setMessage('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('admin_token');
      await axios.post('http://localhost:8080/api/admin/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });

      setStatus('success');
      setMessage('Tài liệu đã được phân tích và lưu trữ thành công!');
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      fetchData(); // Refresh data after upload
    } catch (error) {
      console.error('Lỗi upload:', error);
      setStatus('error');
      setMessage('Lỗi khi tải lên hoặc phiên làm việc đã hết hạn.');
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        handleLogout();
      }
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN');
  };

  return (
    <Container className="py-5">
      <Row className="mb-4">
        <Col className="d-flex justify-content-between align-items-center">
          <h2 className="text-primary">
            <i className="bi bi-database-fill-gear me-2"></i>
            Quản Lý Dữ Liệu Knowledge Base
          </h2>
          <Button variant="outline-danger" onClick={handleLogout}>
            <i className="bi bi-box-arrow-right me-2"></i> Đăng xuất
          </Button>
        </Col>
      </Row>

      {/* Statistics cards */}
      <Row className="mb-4">
        <Col md={4}>
          <Card className="bg-primary text-white shadow">
            <Card.Body>
              <h5><i className="bi bi-chat-dots me-2"></i>Tổng tin nhắn</h5>
              <h2 className="mb-0">{stats.totalChats}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="bg-success text-white shadow">
            <Card.Body>
              <h5><i className="bi bi-file-earmark-text me-2"></i>Tài liệu đã nạp</h5>
              <h2 className="mb-0">{stats.totalUploads}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="bg-white text-dark shadow border-0 h-100">
            <Card.Body>
              <h5 className="text-primary"><i className="bi bi-bar-chart-fill me-2"></i>Mức độ hài lòng</h5>
              <div className="mt-3">
                <div className="d-flex justify-content-between mb-1">
                  <small className="text-success"><i className="bi bi-hand-thumbs-up-fill me-1"></i>Hài lòng ({stats.totalLikes})</small>
                  <small className="text-danger"><i className="bi bi-hand-thumbs-down-fill me-1"></i>Chưa tốt ({stats.totalDislikes})</small>
                </div>
                <div className="progress" style={{ height: '10px' }}>
                  <div 
                    className="progress-bar bg-success" 
                    role="progressbar" 
                    style={{ width: `${stats.totalLikes + stats.totalDislikes === 0 ? 50 : (stats.totalLikes / (stats.totalLikes + stats.totalDislikes)) * 100}%` }}
                  ></div>
                  <div 
                    className="progress-bar bg-danger" 
                    role="progressbar" 
                    style={{ width: `${stats.totalLikes + stats.totalDislikes === 0 ? 50 : (stats.totalDislikes / (stats.totalLikes + stats.totalDislikes)) * 100}%` }}
                  ></div>
                </div>
                <div className="text-center mt-2">
                  <small className="text-muted">Tổng số lượt đánh giá: {stats.totalLikes + stats.totalDislikes}</small>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="justify-content-center">
        <Col md={12}>
          <Card className="shadow-sm border-0">
            <Card.Body className="p-4">
              <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)} className="mb-4">
                
                {/* Tab 1: Upload File */}
                <Tab eventKey="upload" title={<span><i className="bi bi-upload me-2"></i>Nạp Tài Liệu Mới</span>}>
                  <div className="text-center p-3">
                    <p className="text-muted mb-4">
                      Hệ thống hỗ trợ nạp dữ liệu từ các file PDF, DOCX, TXT. 
                      Dữ liệu sau khi tải lên sẽ được băm (embedding) và lưu trữ vào Vector Database (Chroma) để Chatbot sử dụng.
                    </p>

                    <div 
                      className="border rounded p-5 mb-4 bg-light mx-auto"
                      style={{ borderStyle: 'dashed !important', cursor: 'pointer', maxWidth: '600px' }}
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <input 
                        type="file" 
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        accept=".pdf,.txt,.docx"
                        hidden
                      />
                      
                      {file ? (
                        <div>
                          <i className="bi bi-file-earmark-pdf-fill text-danger display-4"></i>
                          <h5 className="mt-3">{file.name}</h5>
                          <p className="text-muted mb-0">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                      ) : (
                        <div>
                          <i className="bi bi-cloud-arrow-up text-primary display-4"></i>
                          <h5 className="mt-3">Click để chọn tài liệu</h5>
                          <p className="text-muted mb-0">Hỗ trợ: PDF, DOCX, TXT (Tối đa 10MB)</p>
                        </div>
                      )}
                    </div>

                    {status === 'success' && (
                      <Alert variant="success" className="text-start mx-auto" style={{maxWidth: '600px'}}>
                        <i className="bi bi-check-circle-fill me-2"></i> {message}
                      </Alert>
                    )}

                    {status === 'error' && (
                      <Alert variant="danger" className="text-start mx-auto" style={{maxWidth: '600px'}}>
                        <i className="bi bi-exclamation-triangle-fill me-2"></i> {message}
                      </Alert>
                    )}

                    <Button 
                      variant="primary" 
                      size="lg" 
                      className="w-100 mx-auto d-block"
                      style={{maxWidth: '600px'}}
                      onClick={handleUpload}
                      disabled={!file || status === 'uploading'}
                    >
                      {status === 'uploading' ? (
                        <><Spinner animation="border" size="sm" className="me-2" /> Đang nhúng dữ liệu vào AI...</>
                      ) : (
                        <><i className="bi bi-upload me-2"></i> Bắt đầu Tải lên</>
                      )}
                    </Button>
                  </div>
                </Tab>

                {/* Tab 2: Upload History */}
                <Tab eventKey="history" title={<span><i className="bi bi-clock-history me-2"></i>Lịch sử Nạp Dữ Liệu</span>}>
                  <Table responsive hover className="align-middle">
                    <thead className="table-light">
                      <tr>
                        <th>ID</th>
                        <th>Tên File</th>
                        <th>Thời gian</th>
                        <th>Người nạp</th>
                        <th>Trạng thái</th>
                      </tr>
                    </thead>
                    <tbody>
                      {uploadHistory.length === 0 ? (
                        <tr><td colSpan="5" className="text-center py-4">Chưa có dữ liệu</td></tr>
                      ) : (
                        uploadHistory.map((item) => (
                          <tr key={item.id}>
                            <td>{item.id}</td>
                            <td className="fw-bold"><i className="bi bi-file-earmark-text text-primary me-2"></i>{item.fileName}</td>
                            <td>{formatDate(item.uploadTime)}</td>
                            <td><Badge bg="secondary">{item.adminUsername}</Badge></td>
                            <td>
                              <Badge bg={item.status === 'Success' ? 'success' : 'danger'}>
                                {item.status}
                              </Badge>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </Table>
                </Tab>

                {/* Tab 3: Chat History */}
                <Tab eventKey="chats" title={<span><i className="bi bi-chat-left-text me-2"></i>Giám sát AI Chatbot</span>}>
                  <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                    <Table responsive hover striped className="align-middle border">
                      <thead className="table-dark" style={{ position: 'sticky', top: 0, zIndex: 1 }}>
                        <tr>
                          <th style={{width: '15%'}}>Thời gian</th>
                          <th style={{width: '10%'}}>Session ID</th>
                          <th style={{width: '25%'}}>Câu hỏi của User</th>
                          <th style={{width: '30%'}}>AI Trả lời</th>
                          <th style={{width: '10%'}}>Đánh giá</th>
                          <th style={{width: '10%'}}>Góp ý</th>
                        </tr>
                      </thead>
                      <tbody>
                        {chatHistory.length === 0 ? (
                          <tr><td colSpan="6" className="text-center py-4">Chưa có cuộc trò chuyện nào</td></tr>
                        ) : (
                          chatHistory.map((chat) => (
                            <tr key={chat.id}>
                              <td className="text-muted" style={{fontSize: '0.85rem'}}>{formatDate(chat.chatTime)}</td>
                              <td><Badge bg="info" className="text-truncate" style={{maxWidth: '100px'}}>{chat.userIdentifier}</Badge></td>
                              <td className="fw-bold">{chat.question}</td>
                              <td style={{fontSize: '0.9rem', whiteSpace: 'pre-wrap', maxHeight: '100px', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical'}}>{chat.answer}</td>
                              <td className="text-center">
                                {chat.isLiked === true && <Badge bg="success"><i className="bi bi-hand-thumbs-up-fill me-1"></i>Thích</Badge>}
                                {chat.isLiked === false && <Badge bg="danger"><i className="bi bi-hand-thumbs-down-fill me-1"></i>Không thích</Badge>}
                                {(chat.isLiked === null || chat.isLiked === undefined) && <span className="text-muted">-</span>}
                              </td>
                              <td style={{fontSize: '0.85rem', fontStyle: 'italic', maxWidth: '150px'}} className="text-truncate">{chat.feedback || '-'}</td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </Table>
                  </div>
                </Tab>

              </Tabs>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default AdminDashboard;
