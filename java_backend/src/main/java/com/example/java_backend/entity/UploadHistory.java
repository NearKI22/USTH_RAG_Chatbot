package com.example.java_backend.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "upload_history")
public class UploadHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Tên Admin đã upload file
    @Column(name = "admin_username", nullable = false)
    private String adminUsername;

    @Column(name = "file_name", nullable = false)
    private String fileName;

    @Column(name = "upload_time", nullable = false)
    private LocalDateTime uploadTime;

    // Trạng thái: "Processing", "Success", "Failed"
    @Column(nullable = false)
    private String status;

    public UploadHistory() {
    }

    public UploadHistory(String adminUsername, String fileName, String status) {
        this.adminUsername = adminUsername;
        this.fileName = fileName;
        this.status = status;
        this.uploadTime = LocalDateTime.now();
    }

    // Getters & Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getAdminUsername() { return adminUsername; }
    public void setAdminUsername(String adminUsername) { this.adminUsername = adminUsername; }

    public String getFileName() { return fileName; }
    public void setFileName(String fileName) { this.fileName = fileName; }

    public LocalDateTime getUploadTime() { return uploadTime; }
    public void setUploadTime(LocalDateTime uploadTime) { this.uploadTime = uploadTime; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
