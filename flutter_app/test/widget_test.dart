import 'package:flutter_test/flutter_test.dart';
import 'package:pet_feeder_app/main.dart';

void main() {
  testWidgets('App starts', (WidgetTester tester) async {
    await tester.pumpWidget(const PetFeederApp());
    expect(find.text('Pet Feeder'), findsOneWidget);
  });
}
