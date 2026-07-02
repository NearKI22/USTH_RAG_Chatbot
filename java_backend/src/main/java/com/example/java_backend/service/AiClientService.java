package com.example.java_backend.service;

import com.example.java_backend.dto.ChatRequestDTO;
import com.example.java_backend.dto.ChatResponseDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;

@Service
public class AiClientService {

    @Autowired
    private RestTemplate restTemplate;

    // Base URL of the FastAPI AI service
    private final String FASTAPI_URL = "http://localhost:8000/ask";

    /**
     * Sends a chat request to the Python FastAPI server and returns the response.
     */
    public ChatResponseDTO getAnswerFromAI(ChatRequestDTO requestDTO) {
        try {
            ResponseEntity<ChatResponseDTO> response = restTemplate.postForEntity(
                    FASTAPI_URL,
                    requestDTO,
                    ChatResponseDTO.class);

            return response.getBody();

        } catch (Exception e) {
            // Python AI service is unreachable — return a fallback error response
            ChatResponseDTO errorResponse = new ChatResponseDTO();
            errorResponse.setAnswer("Unable to reach the AI backend: " + e.getMessage());
            errorResponse.setStatus("error");
            return errorResponse;
        }
    }

    // URL for the document indexing endpoint in Python
    private final String FASTAPI_UPLOAD_URL = "http://localhost:8000/index";

    /**
     * Forwards the uploaded file from AdminController to the Python AI service.
     */
    public String uploadFileToAI(org.springframework.web.multipart.MultipartFile file) {
        try {
            org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
            headers.setContentType(org.springframework.http.MediaType.MULTIPART_FORM_DATA);

            // Wrap the file resource into a multipart form body
            org.springframework.util.MultiValueMap<String, Object> body = new org.springframework.util.LinkedMultiValueMap<>();
            body.add("file", file.getResource());

            org.springframework.http.HttpEntity<org.springframework.util.MultiValueMap<String, Object>> requestEntity =
                    new org.springframework.http.HttpEntity<>(body, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(FASTAPI_UPLOAD_URL, requestEntity, String.class);

            return "File forwarded to Python AI successfully. Response: " + response.getBody();
        } catch (Exception e) {
            return "Failed to forward file to Python AI: " + e.getMessage();
        }
    }
}
