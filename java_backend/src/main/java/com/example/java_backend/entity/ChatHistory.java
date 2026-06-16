package com.example.java_backend.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "chat_history")
public class ChatHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Lưu IP hoặc SessionId của User (nếu cần phân biệt ai đang chat)
    @Column(name = "user_identifier")
    private String userIdentifier;

    // Sử dụng kiểu TEXT để lưu trữ câu hỏi dài
    @Column(columnDefinition = "TEXT", nullable = false)
    private String question;

    // Sử dụng kiểu TEXT để lưu trữ câu trả lời từ AI
    @Column(columnDefinition = "TEXT", nullable = false)
    private String answer;

    @Column(name = "chat_time", nullable = false)
    private LocalDateTime chatTime;

    // Phản hồi của người dùng
    @Column(name = "is_liked")
    private Boolean isLiked; // null: chưa đánh giá, true: like, false: dislike

    @Column(columnDefinition = "TEXT")
    private String feedback; // Ý kiến đóng góp thêm

    // Default Constructor
    public ChatHistory() {
    }

    // Constructor tiện lợi
    public ChatHistory(String userIdentifier, String question, String answer) {
        this.userIdentifier = userIdentifier;
        this.question = question;
        this.answer = answer;
        this.chatTime = LocalDateTime.now(); // Tự động lấy giờ hiện tại
    }

    // Getters & Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getUserIdentifier() { return userIdentifier; }
    public void setUserIdentifier(String userIdentifier) { this.userIdentifier = userIdentifier; }

    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }

    public String getAnswer() { return answer; }
    public void setAnswer(String answer) { this.answer = answer; }

    public LocalDateTime getChatTime() { return chatTime; }
    public void setChatTime(LocalDateTime chatTime) { this.chatTime = chatTime; }

    public Boolean getIsLiked() { return isLiked; }
    public void setIsLiked(Boolean isLiked) { this.isLiked = isLiked; }

    public String getFeedback() { return feedback; }
    public void setFeedback(String feedback) { this.feedback = feedback; }
}
