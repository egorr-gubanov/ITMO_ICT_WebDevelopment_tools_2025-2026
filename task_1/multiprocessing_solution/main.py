import multiprocessing
import time


def calculate_sum(start, end):
    return (start + end) * (end - start + 1) // 2


def worker(args):
    start, end = args
    return calculate_sum(start, end)


def main():
    total = 10000000000000
    num_processes = multiprocessing.cpu_count()
    chunk_size = total // num_processes

    ranges = []
    for i in range(num_processes):
        start_num = i * chunk_size + 1
        end_num = (i + 1) * chunk_size if i < num_processes - 1 else total
        ranges.append((start_num, end_num))

    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(worker, ranges)

    total_sum = sum(results)
    end_time = time.perf_counter()

    print(f"Количество процессов: {num_processes}")
    print(f"Сумма чисел от 1 до {total}: {total_sum}")
    print(f"Время выполнения: {end_time - start_time:.6f} секунд")


if __name__ == "__main__":
    main()
