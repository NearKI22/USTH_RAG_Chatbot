package com.example.java_backend.security;

import com.example.java_backend.entity.AdminUser;
import com.example.java_backend.repository.AdminUserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import java.util.ArrayList;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    @Autowired
    private AdminUserRepository adminUserRepository;

    // Hàm này được Spring Security gọi để lấy thông tin user từ DB
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        AdminUser admin = adminUserRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("Không tìm thấy Admin: " + username));
        
        // Trả về đối tượng User của Spring Security
        return new User(admin.getUsername(), admin.getPassword(), new ArrayList<>());
    }
}
