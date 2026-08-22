srpm:
	python3 get-latest-versions.py --update-specs || true
	rpkg srpm --outdir=$(outdir) --spec=$(spec)
