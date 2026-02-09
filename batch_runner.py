import time
import concurrent.futures
import repo
import orchestrator

# A wrapper function to handle errors for a single user
def process_single_user(consumer_id):
    try:
        # In a real batch, we might fetch the smart reading inside the orchestrator
        # independent of the API inputs.
        # For this demo, we assume the orchestrator handles the lookups.
        
        start_t = time.time()
        filename = orchestrator.generate_invoice(consumer_id)
        duration = time.time() - start_t
        
        if filename:
            return f"✅ {consumer_id}: Success ({duration:.2f}s)"
        else:
            return f"⚠️ {consumer_id}: Skipped/Failed"
            
    except Exception as e:
        return f"❌ {consumer_id}: Critical Error - {str(e)}"

def run_monthly_batch_job():
    print("--- 🏭 STARTING MONTHLY BILLING BATCH ---")
    start_time = time.time()

    # 1. Fetch All Target Users
    print("1. Fetching Consumer List...")
    all_consumers = repo.get_all_consumer_ids()
    print(f"   Found {len(all_consumers)} consumers to bill.")

    # 2. Parallel Processing (The System Design Magic)
    # We use 'ProcessPool' because PDF generation is CPU intensive.
    # max_workers=4 means run 4 bills at the EXACT same time.
    results = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        # Submit all tasks to the pool
        future_to_user = {executor.submit(process_single_user, cid): cid for cid in all_consumers}
        
        # As they finish, print results
        for future in concurrent.futures.as_completed(future_to_user):
            res_string = future.result()
            print(res_string)
            results.append(res_string)

    # 3. Summary Stats
    total_time = time.time() - start_time
    success_count = len([r for r in results if "✅" in r])
    fail_count = len(results) - success_count
    
    print("\n--- 🏁 BATCH COMPLETE ---")
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"Throughput: {len(all_consumers) / total_time:.2f} bills/sec")
    print(f"Success: {success_count} | Failed: {fail_count}")

if __name__ == "__main__":
    run_monthly_batch_job()