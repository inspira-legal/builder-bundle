# Step 5: reproduce, only when the cause needs proof

Run this step when the evidence fits a cause but doesn't prove it: a `plausible` verdict, two
causes the logs can't tell apart, or a fix that needs a failing test to aim at. When the logs
already prove the cause, skip it.

Never load a production configuration or credential here. When the reproduction would need one,
refuse it, and run with a local or development configuration instead.

## Pick the cheapest proof

| the cause                                    | the proof                                               |
| -------------------------------------------- | ------------------------------------------------------- |
| a code path that fails on some input         | a test that fails before the fix, on the current branch |
| a change between the deployed commit and now | a comparison against the default branch at both commits |
| the instance's limits (memory, timeout)      | the production image locally, with the cloud limits     |

## A test that fails before the fix

Write the smallest test that reproduces the anchor's failure with invented data, in the
repository's own test setup, and run it. It has to fail for the reason the hypothesis names, not
for a missing fixture. This test is the one the "fix now" path makes pass.

## The production image, locally

Pull the image the failing revision runs, into the run directory's record, so `close` deletes it:

```bash
python3 scripts/gcloud_read.py pull RUN_DIR IMAGE@DIGEST
```

Run it with the limits the service description printed (memory, CPU, concurrency, timeout), and
a configuration from the repository's local or development example file:

```bash
docker run --rm --memory 512m --cpus 1 --env-file .env.example -p 8080:8080 IMAGE@DIGEST
```

The image's layers can carry configuration. Don't print its environment, its history or its
files into the conversation: the run needs the image's behavior, not its contents. When the
service won't start without a value only production holds, stop the reproduction and say which
value; the report calls the cause `plausible` with what would settle it.

## What the step returns

The command, the configuration it ran with (a file name, never its values), what it did, and
whether that matches the anchor. A reproduction that matches turns the cause into `confirmed`;
one that doesn't is evidence against it, and goes into the report as such.
