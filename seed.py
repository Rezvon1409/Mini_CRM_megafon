from database import SessionLocal
import auth
from models import User, UserRole

def seed_admin_user():
    db = SessionLocal()
    try: 
        admin_exists = db.query(User).filter(User.username == 'Rezvon').first()

        if not admin_exists:
            print('⏳ Creating admin (Rezvon)...')
            hashed_pwd = auth.get_password_hash('AdminRezvon0880')

            initial_admin = User(
                username='Rezvon', 
                email='rezvon0880@gmail.com', 
                full_name='Umed Rajabov', 
                role=UserRole.superadmin,  
                hashed_password=hashed_pwd, 
                is_active=True
            )
            db.add(initial_admin)
            db.commit()
            print('Admin created successfully. Login: Rezvon , Password: AdminRezvon0880')
        else: 
            print('Admin (Rezvon) already exists in database.')
    except Exception as e:
        print(f'Error in creating Admin: {e}')
    finally:
        db.close()