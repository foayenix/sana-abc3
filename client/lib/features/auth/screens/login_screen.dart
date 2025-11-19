// Re-export the connected version
export 'login_screen_connected.dart' show LoginScreenConnected;

import 'package:flutter/material.dart';
import 'login_screen_connected.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const LoginScreenConnected();
  }
}
