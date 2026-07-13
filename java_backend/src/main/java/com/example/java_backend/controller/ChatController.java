package com.example.java_backend.controller;

import com.example.java_backend.dto.ChatRequestDTO;
import com.example.java_backend.dto.ChatResponseDTO;
import com.example.java_backend.dto.FeedbackRequestDTO;
import com.example.java_backend.entity.ChatHistory;
import com.example.java_backend.repository.ChatHistoryRepository;
import com.example.java_backend.service.AiClientService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api")
public class ChatController {

    @Autowired
    private AiClientService aiClientService;
    
    @Autowired
    private ChatHistoryRepository chatHistoryRepository;

    /**
     * Endpoint: POST http://localhost:8080/api/chat
     * Question go to here
     * Take JSON (requestDTO), send to Service to process, then return result to Web.
     */
    @PostMapping("/chat")
    public ChatResponseDTO chatWithAI(@RequestBody ChatRequestDTO requestDTO, HttpServletRequest request) {

        System.out.println(">>> Java Web received your question: " + requestDTO.getQuery());

        // Get user identifier from sessionId or fallback to IP address
        String userIdentifier = requestDTO.getSessionId();
        if (userIdentifier == null || userIdentifier.trim().isEmpty()) {
            userIdentifier = request.getRemoteAddr();
        }

        // Call Service to get answer from Python
        ChatResponseDTO response = aiClientService.getAnswerFromAI(requestDTO);

        System.out.println("<<< Answer from Python: " + response.getAnswer());
        
        // Save chat history to database
        try {
            // Use originalQuestion (clean, short) for storing; fall back to query if not provided
            String questionToStore = (requestDTO.getOriginalQuestion() != null && !requestDTO.getOriginalQuestion().isBlank())
                    ? requestDTO.getOriginalQuestion()
                    : requestDTO.getQuery();
            ChatHistory history = new ChatHistory(userIdentifier, questionToStore, response.getAnswer());
            history = chatHistoryRepository.save(history);
            System.out.println(">>> Saved chat history to Database");
            
            // Assign ID so frontend can update feedback
            response.setHistoryId(history.getId());
        } catch (Exception e) {
            System.out.println("Error saving chat history: " + e.getMessage());
        }

        return response;
    }

    /**
     * Endpoint: GET http://localhost:8080/api/chat/history
     * Retrieves chat history for a specific sessionId
     */
    @GetMapping("/chat/history")
    public List<ChatHistory> getChatHistory(@RequestParam String sessionId, HttpServletRequest request) {
        String identifier = (sessionId != null && !sessionId.trim().isEmpty()) ? sessionId : request.getRemoteAddr();
        return chatHistoryRepository.findByUserIdentifierOrderByChatTimeAsc(identifier);
    }

    /**
     * Endpoint: POST http://localhost:8080/api/chat/feedback
     * Updates feedback and like/dislike status for a specific answer.
     */
    @PostMapping("/chat/feedback")
    public String updateFeedback(@RequestBody FeedbackRequestDTO feedbackDTO) {
        if (feedbackDTO.getHistoryId() == null) {
            return "Missing historyId";
        }
        
        ChatHistory history = chatHistoryRepository.findById(feedbackDTO.getHistoryId()).orElse(null);
        if (history != null) {
            history.setIsLiked(feedbackDTO.getIsLiked());
            history.setFeedback(feedbackDTO.getFeedback());
            chatHistoryRepository.save(history);
            return "Feedback updated successfully";
        } else {
            return "Chat history not found";
        }
    }
}
