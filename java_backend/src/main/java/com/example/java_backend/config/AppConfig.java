package com.example.java_backend.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class AppConfig {

    /**
     * Create RestTemplate
     * Purpose: để gọi các HTTP Request (GET, POST,...) sang một hệ thống khác
     * (Python).
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
