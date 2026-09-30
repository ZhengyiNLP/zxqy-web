"""
数据库种子数据模块

功能描述：
- 默认管理员账号创建
- 权限系统初始化（角色、权限、预置数据）

被 database.init_db() 调用。
"""
import logging

logger = logging.getLogger("seed")


def run_seed(SessionLocal):
    """Initialize seed data: admin user + permission system."""
    from models import User, Permission, Role, RolePermission, UserRole
    from auth import hash_password

    db = SessionLocal()
    try:
        # Default admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                display_name="管理员",
                is_admin=True,
                is_super_admin=True,
                must_change_password=False,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.warning("=" * 50)
            logger.warning("⚠️  默认管理员账号已创建：admin / admin123")
            logger.warning("⚠️  请立即登录并修改默认密码！")
            logger.warning("=" * 50)
        else:
            if not admin.is_super_admin:
                admin.is_super_admin = True
                db.commit()
                logger.info("Set is_super_admin=True for admin user")

        # Initialize permission system
        _init_permission_system(db)

        # Initialize business data
        _init_business_data(db)

        db.commit()
    finally:
        db.close()


def _init_permission_system(db):
    """Initialize permission system data"""
    from models import Permission, Role, RolePermission, UserRole, User

    # Check if permissions already initialized
    existing_count = db.query(Permission).count()
    if existing_count > 0:
        # Ensure admin user has super_admin role
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            super_admin_role = db.query(Role).filter(Role.code == "super_admin").first()
            if super_admin_role:
                existing = db.query(UserRole).filter(
                    UserRole.user_id == admin.id,
                    UserRole.role_id == super_admin_role.id
                ).first()
                if not existing:
                    db.add(UserRole(user_id=admin.id, role_id=super_admin_role.id))
                    logger.info("Assigned super_admin role to admin user")

        # Assign all permissions to super_admin
        super_admin_role = db.query(Role).filter(Role.code == "super_admin").first()
        if super_admin_role:
            existing_role_perms = set(
                rp.permission_id for rp in db.query(RolePermission).filter(RolePermission.role_id == super_admin_role.id).all()
            )
            for perm in db.query(Permission).all():
                if perm.id not in existing_role_perms:
                    db.add(RolePermission(role_id=super_admin_role.id, permission_id=perm.id))

        db.commit()
        return

    logger.info("Initializing permission system...")

    # 1. Insert permissions (three-level format: module:resource:action)
    #    框架骨架只包含系统管理相关权限，业务权限在各自模块中添加
    permissions_data = [
        # system:user
        ("system", "user", "list", "查看用户列表", "查看系统用户列表"),
        ("system", "user", "add", "创建用户", "创建新用户账号"),
        ("system", "user", "edit", "编辑用户", "编辑用户信息"),
        ("system", "user", "delete", "删除用户", "删除用户账号"),
        ("system", "user", "reset-password", "重置密码", "重置用户密码"),
        # system:role
        ("system", "role", "list", "查看角色列表", "查看系统角色列表"),
        ("system", "role", "add", "创建角色", "创建新角色"),
        ("system", "role", "edit", "编辑角色", "编辑角色信息"),
        ("system", "role", "delete", "删除角色", "删除角色"),
        ("system", "role", "assign", "分配角色", "为用户分配角色"),
        # auth:profile
        ("auth", "profile", "view", "查看个人信息", "查看个人资料和权限"),
        ("auth", "profile", "edit", "编辑个人信息", "编辑个人资料"),
        # auth:password
        ("auth", "password", "change", "修改密码", "修改个人密码"),
        # system:menu
        ("system", "menu", "view", "查看菜单", "查看系统菜单"),
        # setting:config
        ("setting", "config", "list", "查看系统参数", "查看系统参数配置"),
        ("setting", "config", "add", "新增系统参数", "新增系统参数配置"),
        ("setting", "config", "edit", "编辑系统参数", "编辑系统参数配置"),
        ("setting", "config", "delete", "删除系统参数", "删除系统参数配置"),
    ]

    for module, resource, action, name, desc in permissions_data:
        db.add(Permission(module=module, resource=resource, action=action, name=name, description=desc))
    db.flush()

    # 2. Insert roles
    roles_data = [
        ("super_admin", "超级管理员", "拥有所有权限，可管理整个系统", True),
        ("admin", "管理员", "管理用户和系统设置", False),
        ("user", "普通用户", "基本功能访问", False),
    ]

    for code, name, desc, is_system in roles_data:
        db.add(Role(code=code, name=name, description=desc, is_system=is_system))
    db.flush()

    # 3. Assign all permissions to super_admin
    super_admin_role = db.query(Role).filter(Role.code == "super_admin").first()
    all_permissions = db.query(Permission).all()
    for perm in all_permissions:
        db.add(RolePermission(role_id=super_admin_role.id, permission_id=perm.id))

    # 4. Assign permissions to admin role
    admin_role = db.query(Role).filter(Role.code == "admin").first()
    admin_permission_keys = [
        "system:user:list", "system:user:add", "system:user:edit", "system:user:delete", "system:user:reset-password",
        "system:role:list", "system:role:add", "system:role:edit", "system:role:delete", "system:role:assign",
        "auth:profile:view", "auth:profile:edit", "auth:password:change",
        "system:menu:view",
        "setting:config:list", "setting:config:add", "setting:config:edit", "setting:config:delete",
    ]
    for perm_key in admin_permission_keys:
        parts = perm_key.split(":")
        perm = db.query(Permission).filter(
            Permission.module == parts[0],
            Permission.resource == parts[1],
            Permission.action == parts[2],
        ).first()
        if perm:
            db.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))

    # 5. Assign basic permissions to user role
    user_role = db.query(Role).filter(Role.code == "user").first()
    user_permission_keys = [
        "auth:profile:view", "auth:profile:edit", "auth:password:change",
        "system:menu:view",
    ]
    for perm_key in user_permission_keys:
        parts = perm_key.split(":")
        perm = db.query(Permission).filter(
            Permission.module == parts[0],
            Permission.resource == parts[1],
            Permission.action == parts[2],
        ).first()
        if perm:
            db.add(RolePermission(role_id=user_role.id, permission_id=perm.id))

    # 6. Assign super_admin role to admin user
    admin_user = db.query(User).filter(User.username == "admin").first()
    if admin_user:
        db.add(UserRole(user_id=admin_user.id, role_id=super_admin_role.id))
        logger.info("Assigned super_admin role to admin user")

    logger.info("Permission system initialized successfully")


def _init_business_data(db):
    """Initialize business seed data: categories, pages, site config"""
    from models import Category, Page, Banner, FriendLink, SysConfig

    # Check if already initialized
    if db.query(Category).count() > 0:
        return

    logger.info("Initializing business data...")

    # 1. Categories
    categories = [
        ("企业新闻", "article", 1), ("行业资讯", "article", 2), ("通知公告", "article", 3),
        ("产品分类一", "product", 1), ("产品分类二", "product", 2),
    ]
    for name, type_, sort in categories:
        db.add(Category(name=name, type=type_, sort_order=sort, status=1))

    # 2. Pages
    pages = [
        ("about", "关于我们", "<p>这里是关于我们页面内容，请在后台管理中编辑。</p>", None),
        ("culture", "企业文化", "<p>这里是企业文化页面内容，请在后台管理中编辑。</p>", None),
        ("contact", "联系我们", "<p>这里是联系我们页面内容。</p>",
         '{"address":"请编辑企业地址","phone":"请编辑联系电话","email":"请编辑邮箱","workTime":"周一至周五 9:00-18:00"}'),
    ]
    for key, title, content, extra in pages:
        db.add(Page(page_key=key, title=title, content=content, extra_data=extra))

    # 3. Site config
    configs = [
        ("site_name", "网站名称", "中小企业门户网站", "网站名称"),
        ("site_logo", "网站Logo", "", "网站Logo URL"),
        ("icp", "ICP备案号", "", "ICP备案号"),
        ("home_article_count", "首页动态条数", "6", "首页最新动态展示条数"),
        ("home_product_count", "首页产品条数", "8", "首页产品精选展示条数"),
    ]
    for key, name, value, remark in configs:
        existing = db.query(SysConfig).filter(SysConfig.config_key == key).first()
        if not existing:
            db.add(SysConfig(config_name=name, config_key=key, config_value=value, remark=remark))

    # 4. Sample banner
    db.add(Banner(title="欢迎使用中小企业门户网站", image_url="", link_url="", sort_order=1, status=1))

    logger.info("Business data initialized successfully")
