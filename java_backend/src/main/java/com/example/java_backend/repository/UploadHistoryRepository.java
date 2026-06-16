package com.example.java_backend.repository;

import com.example.java_backend.entity.UploadHistory;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UploadHistoryRepository extends JpaRepository<UploadHistory, Long> {
    List<UploadHistory> findAllByOrderByUploadTimeDesc();
}
