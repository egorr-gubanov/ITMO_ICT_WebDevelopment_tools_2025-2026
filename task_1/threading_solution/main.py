import threading
import time


def calculate_sum(start, end):
    return (start + end) * (end - start + 1) // 2


def worker(start, end, results, lock, index):
    result = calculate_sum(start, end)
    with lock:
        results[index] = result


def main():
    total = 10000000000000
    num_threads = 8
    chunk_size = total // num_threads

    threads = []
    results = [0] * num_threads
    lock = threading.Lock()

    start_time = time.perf_counter()

    for i in range(num_threads):
        start_num = i * chunk_size + 1
        end_num = (i + 1) * chunk_size if i < num_threads - 1 else total
        thread = threading.Thread(target=worker, args=(start_num, end_num, results, lock, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    end_time = time.perf_counter()

    print(f"Количество потоков: {num_threads}")
    print(f"Сумма чисел от 1 до {total}: {total_sum}")
    print(f"Время выполнения: {end_time - start_time:.6f} секунд")


if __name__ == "__main__":
    main()
