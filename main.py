import argparse
#from voc.pipeline import run as run_voc
#from portfolio.pipeline import run as run_portfolio
#from pricing.pipeline import run as run_pricing

def main() -> None:
    parser = argparse.ArgumentParser(description="Customer & Growth AI Lab")
    parser.add_argument("module", choices=["voc", "portfolio", "pricing", "all"])
    args = parser.parse_args()
    if args.module in ("voc", "all"):
        run_voc()
    if args.module in ("portfolio", "all"):
        run_portfolio()
    if args.module in ("pricing", "all"):
        run_pricing()

if __name__ == "__main__":
    main()