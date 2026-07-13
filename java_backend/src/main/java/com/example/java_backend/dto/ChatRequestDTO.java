package com.example.java_backend.dto;

// Hứng user question
public class ChatRequestDTO {

    // Full query sent to AI (may include chat history context)
    private String query;

    // The user's original question (short, stored in DB for display)
    private String originalQuestion;

    // Session identifier
    private String sessionId;

    // Getter/Setter
    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = query;
    }

    public String getOriginalQuestion() {
        return originalQuestion;
    }

    public void setOriginalQuestion(String originalQuestion) {
        this.originalQuestion = originalQuestion;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
}
