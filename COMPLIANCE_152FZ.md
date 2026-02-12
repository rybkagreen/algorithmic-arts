# 152-ФЗ Compliance

## Key Points

✅ **All data stored in Russia** (Yandex Cloud)  
✅ **TLS 1.3 encryption** for all connections  
✅ **Bcrypt password hashing** (cost 12)  
✅ **AES-256 encryption** for sensitive fields  
✅ **Audit logging** of all PD operations  
✅ **User rights**: access, correction, deletion  

## Personal Data Categories

**Processed:**
- Contact info (email, phone)
- Account data (name, company)
- Usage data (activity logs)
- Payment data (billing info)

**NOT Processed:**
- Biometric data
- Health data
- Political/religious views

## User Rights

Users can:
- Export their data (JSON)
- Correct inaccuracies
- Delete account (30 days grace period)
- Revoke consent

## Compliance Checklist

- [x] All servers in RF (Yandex Cloud ru-central1)
- [x] Encrypted data at rest & in transit
- [x] RBAC + ABAC authorization
- [x] Regular security audits
- [x] Privacy policy published
- [x] Roskomnadzor notification filed

**Full Documentation:** See detailed compliance guide.
