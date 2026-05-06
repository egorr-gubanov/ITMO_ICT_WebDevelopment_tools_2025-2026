import asyncio
import time


def calculate_sum(start, end):
    return (start + end) * (end - start + 1) // 2


async def async_calculate_sum(start, end):
    return calculate_sum(start, end)


async def main():
    total = 10000000000000
    num_tasks = 8
    chunk_size = total // num_tasks

    tasks = []
    for i in range(num_tasks):
        start_num = i * chunk_size + 1
        end_num = (i + 1) * chunk_size if i < num_tasks - 1 else total
        tasks.append(async_calculate_sum(start_num, end_num))

    start_time = time.perf_counter()

    results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.perf_counter()

    print(f"Количество задач: {num_tasks}")
    print(f"Сумма чисел от 1 до {total}: {total_sum}")
    print(f"Время выполнения: {end_time - start_time:.6f} секунд")


if __name__ == "__main__":
    asyncio.run(main())
