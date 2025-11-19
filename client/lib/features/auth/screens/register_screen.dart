// Re-export the connected version
export 'register_screen_connected.dart' show RegisterScreenConnected;

import 'package:flutter/material.dart';
import 'register_screen_connected.dart';

class RegisterScreen extends StatelessWidget {
  const RegisterScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const RegisterScreenConnected();
  }
}
