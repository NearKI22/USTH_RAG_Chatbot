package com.example.java_backend.controller;

import com.example.java_backend.dto.LoginRequestDTO;
import com.example.java_backend.dto.LoginResponseDTO;
import com.example.java_backend.security.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.AuthenticationException;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin")
public class AuthController {

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private JwtUtil jwtUtil;

    // Admin login endpoint
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequestDTO request) {
        try {
            // Authenticate via Spring Security
            authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
            );
        } catch (AuthenticationException e) {
            // If authentication fails
            return ResponseEntity.status(401).body(new LoginResponseDTO(null, "Invalid username or password!"));
        }

        // Generate JWT upon success
        String jwtToken = jwtUtil.generateToken(request.getUsername());
        
        // Return token to frontend
        return ResponseEntity.ok(new LoginResponseDTO(jwtToken, "Login successful"));
    }
}
