import json
from datetime import timedelta, datetime
from sqlalchemy import text
import pytest


@pytest.mark.asyncio
async def test_check_api(test_client):
    response = await test_client.get("/coworkings")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_check_api(test_client):
    # print(test_client)
    # await asyncio.sleep(10)
    # print(await test_client.post("/users", json={"username": "test", "email": "test@test.com", "password": "12345678"}))
    # assert True
    # assert False
    # return
    response = await test_client.get("/coworkings")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_register(test_client):
    user_data = {
        "username": "tessstingggg",
        "email": "0zrJsH@example.com",
        "password": "12345678",
    }
    response = await test_client.post(
        "/users",
        json=user_data,
    )

    assert response.status_code == 200
    assert response.json()['username'] == user_data['username']
    assert response.json()['email'] == user_data['email']
    assert response.json()['access_level'] == "GUEST"
    assert response.json()['client_id']


@pytest.mark.asyncio
async def test_auth(test_client):
    async def test_auth_guest(test_client):
        user_data = {
            "email": "guestt@example.com",
            "password": "Adminnn15)!",
            "username": "guest"
        }
        await test_client.post(
            "/users",
            json=user_data,
        )

        user_data = {
            "email": "guestt@example.com",
            "password": "Adminnn15)!",
        }
        response = await test_client.post(
            "/users/auth",
            json=user_data,
        )

        assert response.status_code == 200
        access_token = response.json()['access_token']
        print(access_token)

        response = await test_client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(f"Bearer {access_token}")

        assert response.status_code == 200
        assert response.json()['access_level'] == "GUEST", "wrong access level for guest"

    async def test_auth_student(test_client):
        user_data = {
            "email": "student@example.com",
            "password": "Adminnn15)!",
        }
        response = await test_client.post(
            "/users/auth",
            json=user_data,
        )

        assert response.status_code == 200
        access_token = response.json()['access_token']

        response = await test_client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert response.json()['access_level'] == "STUDENT", "wrong access level for student"

    async def test_auth_admin(test_client):
        user_data = {
            "email": "admin@example.com",
            "password": "Adminnn15)!",
        }
        response = await test_client.post(
            "/users/auth",
            json=user_data,
        )

        assert response.status_code == 200
        access_token = response.json()['access_token']

        response = await test_client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert response.json()['access_level'] == "ADMIN", "wrong access level for admin"

    await test_auth_guest(test_client)
    await test_auth_student(test_client)
    await test_auth_admin(test_client)


@pytest.mark.asyncio
async def test_get_free_seats(test_client, db_session):
    async with db_session as session:
        query = text("""
            INSERT INTO coworkings (coworking_id, title, address, tz_offset)
            VALUES (:coworking_id, :title, :address, :tz_offset)
        """)
        await session.execute(query, {
            "coworking_id": "550e8400-e29b-41d4-a716-446655440000",  # Пример UUID
            "title": "Коворкинг №1",
            "address": "ул. Примерная, 123",
            "tz_offset": 3  # Пример смещения часового пояса
        })
        await session.commit()

        query = text("""
            INSERT INTO seats (seat_uuid, seat_id, coworking_id, seat_access_level, pos_x, pos_y, price, seat_type, width, height, rx, rotation)
            VALUES (:seat_uuid, :seat_id, :coworking_id, :seat_access_level, :pos_x, :pos_y, :price, :seat_type, :width, :height, :rx, :rotation)
        """)
        await session.execute(query, {
            "seat_uuid": "550e8400-e29b-41d4-a716-446655440001",  # Пример UUID
            "seat_id": "1",
            "coworking_id": "550e8400-e29b-41d4-a716-446655440000",  # UUID коворкинга
            "seat_access_level": "GUEST",  # Пример уровня доступа
            "pos_x": 10.5,  # Координата X
            "pos_y": 20.3,  # Координата Y
            "price": 10000,  # Цена в копейках (10000 = 100 рублей)
            "seat_type": "OPENSPACE",
            "width": 1.0,
            "height": 1.0,
            "rx": 0.0,
            "rotation": 0.0
        })
        await session.commit()
    
    response = await test_client.get("/coworkings")
    assert response.status_code == 200
    coworking_id = response.json()[0]['coworking_id']

    async def test_get_free_seats_guest():
        # Проверка свободного места
        user_data = {
            "email": "guest@example.com",
            "password": "Adminnn15)!",
        }
        response = await test_client.post(
            "/users/auth",
            json=user_data,
        )

        access_token = response.json()['access_token']
        response = await test_client.get(
            f"/booking/{coworking_id}/free_seats",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"start_date": "2025-05-01T14:30:00Z", "end_date": "2025-05-01T15:00:00Z"}
        )
        assert response.status_code == 200
        seat_1 = list(filter(lambda x: x['seat_id'] == '1', response.json()))[0]
        assert seat_1['is_free'] == True
        return access_token, seat_1

    async def booking(access_token, seat_1):
        # бронирование места
        response = await test_client.post(
            f"/booking/seat",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "start_date": "2025-05-01T14:30:00Z",
                "end_date": "2025-05-01T15:00:00Z",
                "seats": [
                    {
                        "seat_id": "1",
                        "seat_uuid": seat_1['seat_uuid']
                    }
                ]
            }
        )
        assert response.status_code == 200
        booking_id = response.json()['booking_id']
        return booking_id

    async def after_booking(access_token, booking_id):
        # Проверка, что теперь место забронировано
        response = await test_client.get(
            f"/booking/{coworking_id}/free_seats",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"start_date": "2025-05-01T14:30:00Z", "end_date": "2025-05-01T15:30:00Z"}
        )
        assert response.status_code == 200
        assert list(filter(lambda x: x['seat_id'] == '1', response.json()))[0]['is_free'] == False

        # Проверка, что бронь отображается
        response = await test_client.get(
            f"booking/my/{coworking_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert response.json()[0]['booking_id'] == booking_id
        assert response.json()[0]['start_date'] == "2025-05-01T14:30:00Z"
        assert response.json()[0]['end_date'] == "2025-05-01T15:00:00Z"

        # Перенос бронирования 
        response = await test_client.patch(
            f"/booking/seat/{booking_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "start_date": "2025-05-01T16:00:00Z",
                "end_date": "2025-05-01T16:30:00Z",
            }
        )
        assert response.status_code == 200

        # Проверка переноса
        response = await test_client.get(
            f"booking/my/{coworking_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert response.json()[0]['start_date'] == "2025-05-01T16:00:00Z"
        assert response.json()[0]['end_date'] == "2025-05-01T16:30:00Z"

        # отмена бронирования
        response = await test_client.delete(
            f"/booking/{booking_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 204

        # Проверка, что теперь место свободно
        response = await test_client.get(
            f"/booking/{coworking_id}/free_seats",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"start_date": "2025-05-01T14:30:00Z", "end_date": "2025-05-01T15:30:00Z"}
        )
        assert response.status_code == 200
        assert list(filter(lambda x: x['seat_id'] == '1', response.json()))[0]['is_free'] == True

        # Проверка удаления бронирования
        response = await test_client.get(
            f"booking/my/{coworking_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 0

    access_token, seat_1 = await test_get_free_seats_guest()
    booking_id = await booking(access_token, seat_1)

    await after_booking(access_token, booking_id)


@pytest.mark.asyncio
async def test_admins(test_client):
    response = await test_client.get("/coworkings")
    assert response.status_code == 200

    response = await test_client.post(
        '/users/auth',
        json={
            "email": "admin@example.com",
            "password": "Adminnn15)!"
        }
    )

    assert response.status_code == 200
    access_token = response.json()['access_token']

    async def get_all_clients():
        response = await test_client.get(
            '/admins/all_clients',
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        user_id = response.json()[0]['client_id']

        response = await test_client.get(
            f'/admins/bookings/{user_id}',
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        return user_id

    async def get_all_bookings():
        response = await test_client.get(
            '/admins/bookings',
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200

    await get_all_clients()
    await get_all_bookings()
    await get_all_clients()


@pytest.mark.asyncio
async def test_login_endpoint(test_client):
    # Данные для аутентификации
    login_data = {
        "email": "student@example.com",
        "password": "Adminnn15)!",
    }

    # Вызываем эндпоинт
    response = await test_client.post("/users/auth", json=login_data)

    # Проверяем ответ
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


@pytest.mark.asyncio
async def test_refresh_endpoint(test_client):
    # Сначала получаем refresh_token через аутентификацию
    login_data = {
        "email": "student@example.com",
        "password": "Adminnn15)!",
    }
    login_response = await test_client.post("/users/auth", json=login_data)
    refresh_token = login_response.json()["refresh_token"]

    # Вызываем эндпоинт для обновления токена
    refresh_data = {"refresh_token": refresh_token}
    response = await test_client.post("/users/auth/refresh", json=refresh_data)

    # Проверяем ответ
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


@pytest.mark.asyncio
async def test_booking_flow(test_client, db_session):
    async with db_session as session:
        query = text("""
            INSERT INTO coworkings (coworking_id, title, address, tz_offset)
            VALUES (:coworking_id, :title, :address, :tz_offset)
        """)
        await session.execute(query, {
            "coworking_id": "550e8400-e29b-41d4-a716-446655440000",  # Пример UUID
            "title": "Коворкинг №1",
            "address": "ул. Примерная, 123",
            "tz_offset": 3  # Пример смещения часового пояса
        })
        await session.commit()

        query = text("""
            INSERT INTO seats (seat_uuid, seat_id, coworking_id, seat_access_level, pos_x, pos_y, price, seat_type, width, height, rx, rotation)
            VALUES (:seat_uuid, :seat_id, :coworking_id, :seat_access_level, :pos_x, :pos_y, :price, :seat_type, :width, :height, :rx, :rotation)
        """)
        await session.execute(query, {
            "seat_uuid": "550e8400-e29b-41d4-a716-446655440001",  # Пример UUID
            "seat_id": "1",
            "coworking_id": "550e8400-e29b-41d4-a716-446655440000",  # UUID коворкинга
            "seat_access_level": "GUEST",  # Пример уровня доступа
            "pos_x": 10.5,  # Координата X
            "pos_y": 20.3,  # Координата Y
            "price": 10000,  # Цена в копейках (10000 = 100 рублей)
            "seat_type": "OPENSPACE",
            "width": 1.0,
            "height": 1.0,
            "rx": 0.0,
            "rotation": 0.0
        })
        await session.commit()


    # Register user
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Testpass123!"
    }
    register_response = await test_client.post("/users", json=user_data)

    assert register_response.status_code == 200

    # Authenticate user
    auth_data = {
        "email": "testuser@example.com",
        "password": "Testpass123!"
    }
    auth_response = await test_client.post("/users/auth", json=auth_data)
    access_token = auth_response.json()["access_token"]

    # Get coworking ID
    coworking_response = await test_client.get("/coworkings")
    assert coworking_response.status_code == 200
    coworking_id = coworking_response.json()[0]["coworking_id"]

    # Get free seats
    start_date = "2030-03-03T15:00"
    end_date = "2030-03-03T18:30"
    free_seats_response = await test_client.get(
        f"/booking/{coworking_id}/free_seats",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"start_date": start_date, "end_date": end_date}
    )
    assert free_seats_response.status_code == 200
    seat = free_seats_response.json()[0]

    # Book a seat
    booking_data = {
        "start_date": start_date,
        "end_date": end_date,
        "seats": [{"seat_id": seat["seat_id"], "seat_uuid": seat["seat_uuid"]}]
    }
    booking_response = await test_client.post(
        "/booking/seat",
        headers={"Authorization": f"Bearer {access_token}"},
        json=booking_data
    )
    assert booking_response.status_code == 200
    booking_id = booking_response.json()["booking_id"]

    # Check my bookings
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', coworking_id)
    my_bookings_response = await test_client.get(
        f"/booking/my/{coworking_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert my_bookings_response.status_code == 200
    assert len(my_bookings_response.json()) > 0

    # Delete booking
    delete_booking_response = await test_client.delete(
        f"/booking/{booking_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert delete_booking_response.status_code == 204

    # Verify booking is deleted
    my_bookings_response = await test_client.get(
        f"/booking/my/{coworking_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert my_bookings_response.status_code == 200
    assert len(my_bookings_response.json()) == 0


@pytest.mark.asyncio
async def test_booking_seat_endpoints(test_client, db_session):

    async with db_session as session:
        query = text("""
            INSERT INTO coworkings (coworking_id, title, address, tz_offset)
            VALUES (:coworking_id, :title, :address, :tz_offset)
        """)
        await session.execute(query, {
            "coworking_id": "550e8400-e29b-41d4-a716-446655440000",  # Пример UUID
            "title": "Коворкинг №1",
            "address": "ул. Примерная, 123",
            "tz_offset": 3  # Пример смещения часового пояса
        })
        await session.commit()

        query = text("""
            INSERT INTO seats (seat_uuid, seat_id, coworking_id, seat_access_level, pos_x, pos_y, price, seat_type, width, height, rx, rotation)
            VALUES (:seat_uuid, :seat_id, :coworking_id, :seat_access_level, :pos_x, :pos_y, :price, :seat_type, :width, :height, :rx, :rotation)
        """)
        await session.execute(query, {
            "seat_uuid": "550e8400-e29b-41d4-a716-446655440001",  # Пример UUID
            "seat_id": "1",
            "coworking_id": "550e8400-e29b-41d4-a716-446655440000",  # UUID коворкинга
            "seat_access_level": "GUEST",  # Пример уровня доступа
            "pos_x": 10.5,  # Координата X
            "pos_y": 20.3,  # Координата Y
            "price": 10000,  # Цена в копейках (10000 = 100 рублей)
            "seat_type": "OPENSPACE",
            "width": 1.0,
            "height": 1.0,
            "rx": 0.0,
            "rotation": 0.0
        })
        await session.commit()
    # Register user
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Testpass123!"
    }
    register_response = await test_client.post("/users", json=user_data)
    assert register_response.status_code == 200

    # Authenticate user
    auth_data = {
        "email": "testuser@example.com",
        "password": "Testpass123!"
    }
    auth_response = await test_client.post("/users/auth", json=auth_data)
    assert auth_response.status_code == 200
    access_token = auth_response.json()["access_token"]

    # Get coworking ID
    coworking_response = await test_client.get("/coworkings")
    assert coworking_response.status_code == 200
    coworking_id = coworking_response.json()[0]["coworking_id"]

    # Get free seats
    start_date = "2030-03-03T15:00"
    end_date = "2030-03-03T18:30"
    free_seats_response = await test_client.get(
        f"/booking/{coworking_id}/free_seats",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"start_date": start_date, "end_date": end_date}
    )
    assert free_seats_response.status_code == 200
    seat = free_seats_response.json()[0]

    # Book a seat
    booking_data = {
        "start_date": start_date,
        "end_date": end_date,
        "seats": [{"seat_id": seat["seat_id"], "seat_uuid": seat["seat_uuid"]}]
    }
    booking_response = await test_client.post(
        "/booking/seat",
        headers={"Authorization": f"Bearer {access_token}"},
        json=booking_data
    )
    assert booking_response.status_code == 200
    booking_id = booking_response.json()["booking_id"]

    # Get occupied seat times
    occupied_response = await test_client.get(
        "/booking/seat/occupied",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"seat_uuids": [seat["seat_uuid"]], "days": ["2030-03-03"]}
    )
    assert occupied_response.status_code == 200
    assert isinstance(occupied_response.json(), list)

    # Modify booking
    new_start_date = "2030-03-03T16:00"
    new_end_date = "2030-03-03T19:00"
    patch_data = {
        "start_date": new_start_date,
        "end_date": new_end_date
    }
    patch_response = await test_client.patch(
        f"/booking/seat",
        headers={"Authorization": f"Bearer {access_token}"},
        json=patch_data
    )

    bookings = await test_client.get(
        f"/booking/my/{coworking_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert bookings.status_code == 200

    assert patch_response.status_code == 200


@pytest.mark.asyncio
async def test_add_passport(test_client):
    # Регистрация пользователя
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Testpass123!"
    }
    register_response = await test_client.post("/users", json=user_data)
    assert register_response.status_code == 200

    # Аутентификация пользователя
    auth_data = {
        "email": "testuser@example.com",
        "password": "Testpass123!"
    }
    auth_response = await test_client.post("/users/auth", json=auth_data)
    assert auth_response.status_code == 200
    access_token = auth_response.json()["access_token"]

    # Добавление паспортных данных
    passport_data = {
        "series": "1234",
        "number": "567890",
        "name": "Иванов Иван Иванович"
    }
    passport_response = await test_client.post(
        "/users/add_passport",
        headers={"Authorization": f"Bearer {access_token}"},
        json=passport_data
    )
    assert passport_response.status_code == 200


@pytest.mark.asyncio
async def test_increase_verification(test_client):
    # Аутентификация администратора
    auth_data = {
        "email": "admin@example.com",
        "password": "Adminnn15)!"
    }
    auth_response = await test_client.post("/users/auth", json=auth_data)
    assert auth_response.status_code == 200
    access_token = auth_response.json()["access_token"]

    # Получение списка всех клиентов
    clients_response = await test_client.get(
        "/admins/all_clients",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert clients_response.status_code == 200
    user_id = clients_response.json()[0]["client_id"]

    # Увеличение уровня верификации
    verification_response = await test_client.post(
        f"/admins/increase_verification/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert verification_response.status_code == 200


@pytest.mark.asyncio
async def test_get_occupied_times(test_client, db_session):
    # Добавление тестовых данных в базу
    async with db_session as session:
        query = text("""
            INSERT INTO coworkings (coworking_id, title, address, tz_offset)
            VALUES (:coworking_id, :title, :address, :tz_offset)
        """)
        await session.execute(query, {
            "coworking_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Коворкинг №1",
            "address": "ул. Примерная, 123",
            "tz_offset": 3
        })
        await session.commit()

        query = text("""
            INSERT INTO seats (seat_uuid, seat_id, coworking_id, seat_access_level, pos_x, pos_y, price, seat_type, width, height, rx, rotation)
            VALUES (:seat_uuid, :seat_id, :coworking_id, :seat_access_level, :pos_x, :pos_y, :price, :seat_type, :width, :height, :rx, :rotation)
        """)
        await session.execute(query, {
            "seat_uuid": "550e8400-e29b-41d4-a716-446655440001",
            "seat_id": "1",
            "coworking_id": "550e8400-e29b-41d4-a716-446655440000",
            "seat_access_level": "GUEST",
            "pos_x": 10.5,
            "pos_y": 20.3,
            "price": 10000,
            "seat_type": "OPENSPACE",
            "width": 1.0,
            "height": 1.0,
            "rx": 0.0,
            "rotation": 0.0
        })
        await session.commit()

    # Аутентификация пользователя
    auth_data = {
        "email": "student@example.com",
        "password": "Adminnn15)!"
    }
    auth_response = await test_client.post("/users/auth", json=auth_data)
    assert auth_response.status_code == 200
    access_token = auth_response.json()["access_token"]

    # Получение занятых временных слотов
    occupied_response = await test_client.get(
        "/booking/seat/occupied",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"seat_uuids": ["550e8400-e29b-41d4-a716-446655440001"], "days": ["2030-03-03"]}
    )
    assert occupied_response.status_code == 200
    assert isinstance(occupied_response.json(), list)


@pytest.mark.asyncio
async def test_get_all_bookings_admin(test_client):
    # Аутентификация администратора
    auth_data = {
        "email": "admin@example.com",
        "password": "Adminnn15)!"
    }
    auth_response = await test_client.post("/users/auth", json=auth_data)
    assert auth_response.status_code == 200
    access_token = auth_response.json()["access_token"]

    # Получение всех бронирований
    bookings_response = await test_client.get(
        "/admins/bookings",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert bookings_response.status_code == 200
    assert isinstance(bookings_response.json(), list)


@pytest.mark.asyncio
async def test_get_all_clients_admin(test_client):
    # Аутентификация администратора
    auth_data = {
        "email": "admin@example.com",
        "password": "Adminnn15)!"
    }
    auth_response = await test_client.post("/users/auth", json=auth_data)
    assert auth_response.status_code == 200
    access_token = auth_response.json()["access_token"]

    # Получение всех клиентов
    clients_response = await test_client.get(
        "/admins/all_clients",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert clients_response.status_code == 200
    assert isinstance(clients_response.json(), list)


@pytest.mark.asyncio
async def test_get_current_user(test_client):
    # Аутентификация пользователя
    auth_data = {
        "email": "student@example.com",
        "password": "Adminnn15)!"
    }
    auth_response = await test_client.post("/users/auth", json=auth_data)
    assert auth_response.status_code == 200
    access_token = auth_response.json()["access_token"]

    # Получение информации о текущем пользователе
    user_response = await test_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert user_response.status_code == 200
    assert "email" in user_response.json()
    assert "username" in user_response.json()