import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';

const AdminLogin = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8080/api/admin/login', {
        username,
        password
      });

      const token = response.data.token;
      if (token) {
        localStorage.setItem('admin_token', token);
        navigate('/admin/dashboard');
      }
    } catch (err) {
      setError('Sai tên đăng nhập hoặc mật khẩu!');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col md={6} lg={5}>
          <Card className="shadow-sm border-0 mt-5">
            <Card.Header className="bg-primary text-white text-center py-4">
              <i className="bi bi-shield-lock-fill display-4"></i>
              <h4 className="mt-2 mb-0">Admin Portal</h4>
              <small>Đăng nhập hệ thống quản trị</small>
            </Card.Header>
            <Card.Body className="p-4">
              {error && <Alert variant="danger">{error}</Alert>}
              
              <Form onSubmit={handleLogin}>
                <Form.Group className="mb-3">
                  <Form.Label>Tên đăng nhập</Form.Label>
                  <div className="input-group">
                    <span className="input-group-text bg-light"><i className="bi bi-person-fill"></i></span>
                    <Form.Control
                      type="text"
                      placeholder="Nhập username..."
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                    />
                  </div>
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>Mật khẩu</Form.Label>
                  <div className="input-group">
                    <span className="input-group-text bg-light"><i className="bi bi-key-fill"></i></span>
                    <Form.Control
                      type="password"
                      placeholder="Nhập password..."
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                </Form.Group>

                <Button 
                  variant="primary" 
                  type="submit" 
                  className="w-100 py-2"
                  disabled={isLoading}
                >
                  {isLoading ? <Spinner animation="border" size="sm" /> : 'Đăng Nhập'}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default AdminLogin;
