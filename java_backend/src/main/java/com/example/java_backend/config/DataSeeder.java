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

    // Hàm run này sẽ tự động chạy 1 lần duy nhất ngay khi Spring Boot khởi động xong
    @Override
    public void run(String... args) throws Exception {
        // Kiểm tra xem trong database đã có tài khoản "admin" chưa
        if (adminUserRepository.findByUsername("admin").isEmpty()) {
            
            // Nếu chưa có, tạo mới 1 tài khoản
            AdminUser defaultAdmin = new AdminUser();
            defaultAdmin.setUsername("admin");
            // Mật khẩu "123456" sẽ được băm bảo mật bởi BCrypt trước khi lưu vào DB
            defaultAdmin.setPassword(passwordEncoder.encode("123456"));
            defaultAdmin.setRole("ROLE_ADMIN");

            adminUserRepository.save(defaultAdmin);
            System.out.println(">>> [DATA SEEDER] Đã khởi tạo thành công tài khoản Admin mặc định (admin / 123456)");
        } else {
            System.out.println(">>> [DATA SEEDER] Tài khoản Admin đã tồn tại. Bỏ qua khởi tạo.");
        }
    }
}
