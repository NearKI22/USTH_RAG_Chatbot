package com.example.java_backend.controller;

import com.example.java_backend.entity.UploadHistory;
import com.example.java_backend.entity.ChatHistory;
import com.example.java_backend.repository.UploadHistoryRepository;
import com.example.java_backend.repository.ChatHistoryRepository;
import com.example.java_backend.service.AiClientService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

    @Autowired
    private AiClientService aiClientService;

    @Autowired
    private UploadHistoryRepository uploadHistoryRepository;

    @Autowired
    private ChatHistoryRepository chatHistoryRepository;

    /**
     * Endpoint: POST /api/admin/upload
     * Admin endpoint to upload documents.
     * File will be forwarded to Python AI.
     */
    @PostMapping("/upload")
    public ResponseEntity<?> uploadFile(@RequestParam("file") MultipartFile file) {
        // Extract admin info from JWT
        Object principal = SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        String adminUsername = "unknown";
        if (principal instanceof UserDetails) {
            adminUsername = ((UserDetails) principal).getUsername();
        } else {
            adminUsername = principal.toString();
        }

        // Step 1: Save upload history with "Processing" status
        UploadHistory history = new UploadHistory(adminUsername, file.getOriginalFilename(), "Processing");
        history = uploadHistoryRepository.save(history); // Save and retrieve ID

        try {
            // Step 2: Forward file to Python AI service
            String aiResponse = aiClientService.uploadFileToAI(file);
            
            // Step 3: Update status on success
            history.setStatus("Success");
            uploadHistoryRepository.save(history);
            
            return ResponseEntity.ok("File uploaded successfully. AI message: " + aiResponse);
            
        } catch (Exception e) {
            // Update status on failure
            history.setStatus("Failed");
            uploadHistoryRepository.save(history);
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }

    // 1. Get general statistics
    @GetMapping("/stats")
    public ResponseEntity<?> getAdminStats() {
        long totalUploads = uploadHistoryRepository.count();
        long totalChats = chatHistoryRepository.count();
        long totalLikes = chatHistoryRepository.countByIsLikedTrue();
        long totalDislikes = chatHistoryRepository.countByIsLikedFalse();
        
        Map<String, Long> stats = new HashMap<>();
        stats.put("totalUploads", totalUploads);
        stats.put("totalChats", totalChats);
        stats.put("totalLikes", totalLikes);
        stats.put("totalDislikes", totalDislikes);
        
        return ResponseEntity.ok(stats);
    }

    // 2. Get upload history
    @GetMapping("/uploads")
    public ResponseEntity<List<UploadHistory>> getUploadHistory() {
        return ResponseEntity.ok(uploadHistoryRepository.findAllByOrderByUploadTimeDesc());
    }

    // 3. Get chat history
    @GetMapping("/chats")
    public ResponseEntity<List<ChatHistory>> getChatHistory() {
        return ResponseEntity.ok(chatHistoryRepository.findAllByOrderByChatTimeDesc());
    }
}
