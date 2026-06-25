"""
应用初始化：创建默认团队、超级管理员角色、admin 用户。
幂等设计，已存在则跳过，不会重复创建。
"""
from api.core.security import hash_password
from api.sys.permission import crud as perm_crud
from api.sys.role import crud as role_crud
from api.sys.team import crud as team_crud
from api.sys.user import crud as user_crud
from api.sys.dict import crud as dict_crud
from api.sys.menu import crud as menu_crud
from api.sys.message import crud as msg_crud
from api.sys.todo import crud as todo_crud
from api.sys.schedule import crud as schedule_crud

DEFAULT_PASSWORD = "Admin!123"


def run() -> None:
    _init_role()
    _init_team()
    _init_admin()
    _init_dict()
    _init_menu()
    _init_sample_data()


def _init_role() -> None:
    if role_crud.get_by_code("super_admin"):
        return
    all_perm_ids = [p["id"] for p in perm_crud.list_all()]
    role_crud.create({
        "name": "超级管理员",
        "code": "super_admin",
        "description": "拥有全部权限",
        "permission_ids": all_perm_ids,
    })
    print(f"[init] 角色「超级管理员」已创建，权限数：{len(all_perm_ids)}")


def _init_team() -> None:
    if team_crud.get_by_code("default"):
        return
    team_crud.create({"name": "默认团队", "code": "default", "description": "系统默认团队"})
    print("[init] 团队「默认团队」已创建")


def _init_admin() -> None:
    if user_crud.get_user_by_username("admin"):
        return
    role = role_crud.get_by_code("super_admin")
    team = team_crud.get_by_code("default")
    user_crud.create_user({
        "username": "admin",
        "hashed_password": hash_password(DEFAULT_PASSWORD),
        "nickname": "超级管理员",
        "email": "admin@example.com",
        "disabled": False,
        "role_ids": [role["id"]] if role else [],
        "team_id": team["id"] if team else None,
        "data_scope": "all",
        "department_ids": [],
    })
    print(f"[init] 用户「admin」已创建，默认密码：{DEFAULT_PASSWORD}")


def _init_dict() -> None:
    created = []

    if not dict_crud.get_by_code("system_name"):
        dict_crud.create({
            "name": "系统名称",
            "code": "system_name",
            "value": "AI Admin",
            "type": "string",
            "parent_id": None,
            "sort": 0,
            "description": "登录页和顶部导航显示的系统名称",
        })
        created.append("system_name")

    if not dict_crud.get_by_code("system_logo"):
        dict_crud.create({
            "name": "系统 Logo",
            "code": "system_logo",
            "value": "",
            "type": "string",
            "parent_id": None,
            "sort": 1,
            "description": "系统 Logo 图片地址，支持 http(s) 或 base64",
        })
        created.append("system_logo")

    if created:
        print(f"[init] 字典已创建：{', '.join(created)}")


def _init_menu() -> None:
    if menu_crud.list_all():
        return

    dashboard = menu_crud.create({
        "name": "工作台",
        "path": "/",
        "icon": "dashboard",
        "parent_id": None,
        "sort": 0,
        "api_id": None,
        "permission_ids": [],
    })

    system = menu_crud.create({
        "name": "系统设置",
        "path": "/sys",
        "icon": "settings",
        "parent_id": None,
        "sort": 100,
        "api_id": None,
        "permission_ids": [],
    })

    for index, (name, path, icon) in enumerate([
        ("消息管理", "/sys/message", "message"),
        ("公告管理", "/sys/announcement", "announcement"),
        ("待办管理", "/sys/todo", "todo"),
        ("日程管理", "/sys/schedule", "schedule"),
        ("快捷入口", "/sys/quick-entry", "quick-entry"),
        ("用户管理", "/sys/user", "user"),
        ("团队管理", "/sys/team", "team"),
        ("角色管理", "/sys/role", "role"),
        ("权限管理", "/sys/permission", "permission"),
        ("数据字典", "/sys/dict", "dict"),
        ("API 管理", "/sys/api", "api"),
        ("菜单管理", "/sys/menu", "menu"),
    ], start=1):
        menu_crud.create({
            "name": name,
            "path": path,
            "icon": icon,
            "parent_id": system["id"],
            "sort": index,
            "api_id": None,
            "permission_ids": [],
        })

    print(f"[init] 默认菜单已创建，顶级应用数：2，工作台 ID：{dashboard['id']}")


def _init_sample_data() -> None:
    from api.sys.message.crud import _DB as msg_db
    if msg_db:
        return
    admin = user_crud.get_user_by_username("admin")
    if not admin:
        return
    uid = admin["id"]
    from datetime import datetime, timedelta
    now = datetime.now()

    for title, content, mtype in [
        ("系统初始化完成", "企业级管理系统已成功启动，所有模块运行正常。", "success"),
        ("欢迎使用 AI Admin", "您可以在消息管理页查看和管理所有系统消息。", "info"),
        ("安全提醒", "请及时修改默认密码，以保障账户安全。", "warning"),
    ]:
        msg_crud.create({"user_id": uid, "title": title, "content": content, "type": mtype})

    for title, priority, status, days in [
        ("完善系统权限配置", "high", "pending", 1),
        ("配置数据字典", "medium", "in_progress", 3),
        ("邀请团队成员", "low", "pending", 7),
    ]:
        due = (now + timedelta(days=days)).strftime("%Y-%m-%d")
        todo_crud.create(uid, {"title": title, "description": None, "status": status, "priority": priority, "due_date": due})

    colors = ["#8B5CF6", "#3B82F6", "#10B981"]
    for i, (title, desc) in enumerate([
        ("系统上线评审", "评审新功能上线计划"),
        ("团队周会", "同步本周工作进展"),
        ("权限审计", "定期检查权限配置"),
    ]):
        start = (now + timedelta(days=i+1)).strftime("%Y-%m-%d 10:00")
        end   = (now + timedelta(days=i+1)).strftime("%Y-%m-%d 11:00")
        schedule_crud.create(uid, {"title": title, "description": desc, "start_time": start, "end_time": end, "all_day": False, "color": colors[i]})

    print("[init] 示例消息、待办、日程已创建")


if __name__ == "__main__":
    run()
