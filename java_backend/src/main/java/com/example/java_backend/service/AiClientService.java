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

    // URL to FastAPI backend
    private final String FASTAPI_URL = "http://localhost:8000/ask";

    /**
     * Sends the chat request to the Python FastAPI server.
     * Returns the ChatResponseDTO.
     */
    public ChatResponseDTO getAnswerFromAI(ChatRequestDTO requestDTO) {
        try {
            // Call Python AI
            ResponseEntity<ChatResponseDTO> response = restTemplate.postForEntity(
                    FASTAPI_URL,
                    requestDTO,
                    ChatResponseDTO.class);

            // Return result (body) to Controller
            return response.getBody();

        } catch (Exception e) {
            // If Python AI is not connect -> error
            ChatResponseDTO errorResponse = new ChatResponseDTO();
            errorResponse.setAnswer("Lỗi kết nối tới AI Backend: " + e.getMessage());
            errorResponse.setStatus("error");
            return errorResponse;
        }
    }

    // URL to Python index API (for document upload)
    private final String FASTAPI_UPLOAD_URL = "http://localhost:8000/index";

    /**
     * Forwards the uploaded file from AdminController to Python.
     */
    public String uploadFileToAI(org.springframework.web.multipart.MultipartFile file) {
        try {
            // Set header to MULTIPART_FORM_DATA
            org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
            headers.setContentType(org.springframework.http.MediaType.MULTIPART_FORM_DATA);

            // Wrap file into MultiValueMap for form-data
            org.springframework.util.MultiValueMap<String, Object> body = new org.springframework.util.LinkedMultiValueMap<>();
            body.add("file", file.getResource());

            org.springframework.http.HttpEntity<org.springframework.util.MultiValueMap<String, Object>> requestEntity = new org.springframework.http.HttpEntity<>(body, headers);

            // Send HTTP POST request to Python
            ResponseEntity<String> response = restTemplate.postForEntity(FASTAPI_UPLOAD_URL, requestEntity, String.class);

            return "Upload thành công sang Python AI. Kết quả: " + response.getBody();
        } catch (Exception e) {
            return "Lỗi khi upload sang Python AI: " + e.getMessage();
        }
    }
}
