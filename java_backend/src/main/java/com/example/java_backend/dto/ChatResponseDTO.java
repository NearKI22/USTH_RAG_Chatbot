package com.example.java_backend.dto;

// Nhiệm vụ: Hứng dữ liệu JSON do Python FastAPI trả về.

public class ChatResponseDTO {

    // Variable to save response from AI (Gemini)
    private String answer;

    // Status of request (usually "success")
    private String status;

    // ID của bản ghi lịch sử chat (để update feedback)
    private Long historyId;

    // Getter/Setter
    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Long getHistoryId() {
        return historyId;
    }

    public void setHistoryId(Long historyId) {
        this.historyId = historyId;
    }
}
