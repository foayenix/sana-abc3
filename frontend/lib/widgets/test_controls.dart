import 'package:flutter/material.dart';

class TestControls extends StatelessWidget {
  final VoidCallback? onRun;
  final VoidCallback? onReset;
  final bool isLoading;

  const TestControls({
    super.key,
    this.onRun,
    this.onReset,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        ElevatedButton.icon(
          onPressed: isLoading ? null : onRun,
          icon: isLoading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.play_arrow),
          label: Text(isLoading ? 'Running...' : 'Run Test'),
        ),
        const SizedBox(width: 16),
        OutlinedButton.icon(
          onPressed: isLoading ? null : onReset,
          icon: const Icon(Icons.refresh),
          label: const Text('Reset'),
        ),
      ],
    );
  }
}
