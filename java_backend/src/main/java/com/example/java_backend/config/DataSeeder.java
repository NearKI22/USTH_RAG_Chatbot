package com.example.java_backend.config;

import com.example.java_backend.entity.AdminUser;
import com.example.java_backend.repository.AdminUserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataSeeder implements CommandLineRunner {

    @Autowired
    private AdminUserRepository adminUserRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    // Runs once automatically right after Spring Boot finishes starting up
    @Override
    public void run(String... args) throws Exception {
        // Check whether a default admin account already exists in the database
        if (adminUserRepository.findByUsername("admin").isEmpty()) {

            // No admin found — create a default one
            AdminUser defaultAdmin = new AdminUser();
            defaultAdmin.setUsername("admin");
            // The plain-text password is hashed by BCrypt before being stored
            defaultAdmin.setPassword(passwordEncoder.encode("123456"));
            defaultAdmin.setRole("ROLE_ADMIN");

            adminUserRepository.save(defaultAdmin);
            System.out.println(">>> [DATA SEEDER] Default admin account created successfully (admin / 123456)");
        } else {
            System.out.println(">>> [DATA SEEDER] Admin account already exists. Skipping initialization.");
        }
    }
}
