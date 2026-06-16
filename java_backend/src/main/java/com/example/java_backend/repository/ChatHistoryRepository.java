package com.example.java_backend.repository;

import com.example.java_backend.entity.ChatHistory;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ChatHistoryRepository extends JpaRepository<ChatHistory, Long> {
    List<ChatHistory> findByUserIdentifierOrderByChatTimeAsc(String userIdentifier);

    List<ChatHistory> findAllByOrderByChatTimeDesc();

    long countByIsLikedTrue();
    long countByIsLikedFalse();
}
