package com.example.java_backend.repository;

import com.example.java_backend.entity.AdminUser;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface AdminUserRepository extends JpaRepository<AdminUser, Long> {
    
    // Tìm kiếm Admin theo username
    Optional<AdminUser> findByUsername(String username);
}
