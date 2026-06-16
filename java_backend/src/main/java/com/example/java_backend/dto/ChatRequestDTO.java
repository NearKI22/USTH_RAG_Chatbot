package com.example.java_backend.dto;

// Hứng user question
public class ChatRequestDTO {

    // Save user's question
    private String query;
    
    // Lưu định danh phiên làm việc của user
    private String sessionId;

    // Getter/Setter
    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = query;
    }
    
    public String getSessionId() {
        return sessionId;
    }
    
    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
}
