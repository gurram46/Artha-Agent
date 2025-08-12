# Security Guide for Artha AI

This document outlines the security measures implemented in Artha AI and provides guidance for secure deployment.

## 🔒 Security Features Implemented

### 1. Authentication & Authorization
- **JWT-based authentication** with secure token generation
- **Password policy enforcement**: Minimum 12 characters with complexity requirements
- **Account lockout mechanism**: Protects against brute force attacks
- **Session management**: Secure token refresh and invalidation
- **Password hashing**: bcrypt with salt for secure password storage

### 2. Input Validation & Sanitization
- **SQL injection prevention**: Pattern detection and parameterized queries
- **XSS protection**: Input sanitization and output encoding
- **Path traversal protection**: File path validation
- **Request size limits**: Prevents DoS attacks
- **Content type validation**: Ensures proper data formats

### 3. Rate Limiting
- **Tiered rate limiting**: Different limits for different endpoint types
  - Authentication: 10 requests/minute
  - General API: 100 requests/minute
  - Chat/AI: 30 requests/minute
  - File uploads: 5 requests/minute
- **Global rate limiting**: 500 total requests/minute per client
- **IP-based tracking**: Prevents abuse from single sources

### 4. Security Headers
- **Content Security Policy (CSP)**: Prevents XSS and code injection
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **Strict Transport Security (HSTS)**: Enforces HTTPS in production
- **Referrer Policy**: Controls referrer information leakage

### 5. Data Protection
- **AES-256 encryption**: For sensitive user data at rest
- **Environment variable security**: No hardcoded credentials
- **Database connection security**: Encrypted connections recommended
- **Secure random key generation**: For JWT secrets and encryption keys

## 🚀 Deployment Security Checklist

### Before Deployment

#### 1. Environment Configuration
```bash
# Generate secure keys
python -c "import secrets, base64; print('ENCRYPTION_KEY=' + base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
python -c "import secrets, base64; print('JWT_SECRET_KEY=' + base64.urlsafe_b64encode(secrets.token_bytes(64)).decode())"
```

#### 2. Database Security
- [ ] Change default database passwords
- [ ] Enable SSL/TLS for database connections
- [ ] Configure database firewall rules
- [ ] Set up database backups with encryption

#### 3. Environment Variables
Update your `.env` file with production values:

```env
# Database - Use strong passwords
DATABASE_URL=postgresql://username:STRONG_PASSWORD@host:port/database

# Security - Generate new keys for production
ENCRYPTION_KEY=your-generated-encryption-key
JWT_SECRET_KEY=your-generated-jwt-secret

# CORS - Add your production domains
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# HTTPS - Enable in production
FORCE_HTTPS=true

# Rate Limiting - Configure for production
RATE_LIMIT_WHITELIST=your-monitoring-ips

# Debug - Disable in production
DEBUG=false
```

#### 4. Frontend Configuration
Update `next.config.ts` for your domain:
```typescript
destination: 'https://your-actual-domain.com/:path*',
```

### Production Deployment

#### 1. Server Security
- [ ] Keep server OS updated
- [ ] Configure firewall (only allow necessary ports)
- [ ] Set up SSL/TLS certificates
- [ ] Enable automatic security updates
- [ ] Configure log monitoring

#### 2. Application Security
- [ ] Use HTTPS everywhere
- [ ] Set secure cookie flags
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Set up monitoring and alerting
- [ ] Regular security scans

#### 3. Database Security
- [ ] Regular backups
- [ ] Access control and user permissions
- [ ] Network isolation
- [ ] Audit logging
- [ ] Encryption at rest

## 🔍 Security Monitoring

### Log Monitoring
Monitor these security events:
- Failed authentication attempts
- Rate limit violations
- Input validation failures
- Unusual access patterns
- Error rates and types

### Recommended Tools
- **Application monitoring**: Sentry, DataDog, or New Relic
- **Security scanning**: OWASP ZAP, Nessus
- **Log analysis**: ELK Stack, Splunk
- **Uptime monitoring**: Pingdom, UptimeRobot

## 🛡️ Security Best Practices

### For Developers
1. **Never commit secrets** to version control
2. **Use environment variables** for all configuration
3. **Validate all inputs** at API boundaries
4. **Follow principle of least privilege**
5. **Regular dependency updates**
6. **Code reviews** for security-sensitive changes

### For Deployment
1. **Use HTTPS everywhere**
2. **Regular security updates**
3. **Monitor and alert** on security events
4. **Backup and disaster recovery** plans
5. **Regular penetration testing**
6. **Security incident response** procedures

## 🚨 Incident Response

### If Security Breach Detected
1. **Immediate containment**: Isolate affected systems
2. **Assessment**: Determine scope and impact
3. **Notification**: Inform stakeholders and users if required
4. **Recovery**: Restore systems and data
5. **Lessons learned**: Update security measures

### Emergency Contacts
- Security team: [your-security-team@company.com]
- Infrastructure team: [your-infra-team@company.com]
- Legal/Compliance: [your-legal-team@company.com]

## 📋 Security Audit Checklist

### Monthly Reviews
- [ ] Review access logs for anomalies
- [ ] Check for failed authentication patterns
- [ ] Verify SSL certificate expiration dates
- [ ] Review rate limiting effectiveness
- [ ] Update dependencies with security patches

### Quarterly Reviews
- [ ] Penetration testing
- [ ] Security configuration review
- [ ] Access control audit
- [ ] Backup and recovery testing
- [ ] Security training for team

## 🔗 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Next.js Security](https://nextjs.org/docs/advanced-features/security-headers)

## 📞 Support

For security-related questions or to report vulnerabilities:
- Email: security@artha-ai.com
- Security advisory: [Create GitHub Security Advisory]

---

**Remember**: Security is an ongoing process, not a one-time setup. Regular reviews and updates are essential for maintaining a secure application.